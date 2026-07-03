import re
import json
import logging
import mysql.connector
from datetime import datetime

from config import (
    CUSTOMERS_TABLE, ISSUES_TABLE, LOG_TABLE,
    PII_COLUMN_MAP, NAME_COLUMNS, ID_COLUMNS, NON_NAME_WORDS,
)
from db.pool import get_db
from utils.pii import find_pii, mask_text, normalize, MASK_TAGS

logger = logging.getLogger(__name__)


# ── Init ──────────────────────────────────────────────────────────────────
def init_db():
    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {ISSUES_TABLE} (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            customer_id VARCHAR(50),
            name        VARCHAR(100),
            issue       VARCHAR(100),
            query_text  TEXT,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {LOG_TABLE} (
            id                  INT AUTO_INCREMENT PRIMARY KEY,
            query_text          TEXT,
            predicted_category  VARCHAR(100),
            probability         FLOAT,
            probabilities_json  TEXT,
            detected_names      TEXT,
            response_time_ms    FLOAT,
            created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()


# ── Logging ───────────────────────────────────────────────────────────────
def log_classification(query, category, prob, probs, names, response_time_ms=0):
    try:
        conn   = get_db()
        cursor = conn.cursor()
        cursor.execute(
            f"INSERT INTO {LOG_TABLE} "
            "(query_text, predicted_category, probability, probabilities_json, detected_names, response_time_ms) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (query, category, prob, json.dumps(probs), ", ".join(names) if names else "", response_time_ms),
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        logger.warning(f"log_classification failed: {e}")


# ── Helpers ───────────────────────────────────────────────────────────────
def row_to_dict(cursor, row) -> dict:
    return dict(zip([d[0] for d in cursor.description], row))


def lookup_by_pii(cursor, pii_type, raw_value):
    col = PII_COLUMN_MAP.get(pii_type)
    if not col:
        return None
    val = normalize(pii_type, raw_value)
    if not val:
        return None
    try:
        cursor.execute(
            f"SELECT * FROM {CUSTOMERS_TABLE} WHERE {col} = %s LIMIT 1", (val,)
        )
        row = cursor.fetchone()
        return row_to_dict(cursor, row) if row else None
    except mysql.connector.Error:
        return None


def lookup_by_full_name(cursor, full_name) -> list:
    results, seen = [], set()
    for col in NAME_COLUMNS:
        try:
            cursor.execute(
                f"SELECT * FROM {CUSTOMERS_TABLE} WHERE {col} LIKE %s LIMIT 10",
                (f"%{full_name}%",),
            )
            for row in cursor.fetchall():
                d   = row_to_dict(cursor, row)
                key = json.dumps(d, sort_keys=True, default=str)
                if key not in seen:
                    seen.add(key)
                    results.append(d)
        except mysql.connector.Error:
            pass
    return results


def lookup_by_single_word(cursor, word) -> list:
    results, seen = [], set()
    for col in NAME_COLUMNS:
        try:
            cursor.execute(
                f"SELECT * FROM {CUSTOMERS_TABLE} WHERE {col} LIKE %s LIMIT 5",
                (f"%{word}%",),
            )
            for row in cursor.fetchall():
                d   = row_to_dict(cursor, row)
                key = json.dumps(d, sort_keys=True, default=str)
                if key not in seen:
                    seen.add(key)
                    results.append(d)
        except mysql.connector.Error:
            pass
    return results


def search_customers(cursor, query, extract_names_fn):
    """
    Three-level search:
      1. PII exact match
      2. Full name match
      3. Single word fallback
    Returns (results, match_method, confidence).
    """
    results, seen = [], set()

    def add(record):
        if record:
            key = json.dumps(record, sort_keys=True, default=str)
            if key not in seen:
                seen.add(key)
                results.append(record)

    # Level 1 — PII exact match
    for item in find_pii(query):
        r = lookup_by_pii(cursor, item["type"], item["value"])
        if r:
            add(r)
    if results:
        return results, "pii_exact", "high"

    # Level 2 — Full name match
    names_found = extract_names_fn(query)
    for full_name in names_found:
        for r in lookup_by_full_name(cursor, full_name):
            add(r)
    if results:
        return results, f"full_name:{names_found[0] if names_found else '?'}", "high"

    # Level 3 — Single word fallback
    cleaned = mask_text(query)
    for tag in MASK_TAGS.values():
        cleaned = cleaned.replace(tag, " ")
    candidate_words = [
        w.strip(".,;:!?\"'()")
        for w in cleaned.split()
        if len(w.strip(".,;:!?\"'()")) >= 3
        and w.strip(".,;:!?\"'()").lower() not in NON_NAME_WORDS
    ]
    for word in candidate_words:
        hits = lookup_by_single_word(cursor, word)
        if len(hits) == 1:
            add(hits[0])
            if results:
                return results, f"single_word:{word}", "medium"

    return results, "none", "low"


def save_issue(cursor, conn, customer_name, customer_id, issue, query_text):
    try:
        cursor.execute(
            f"INSERT INTO {ISSUES_TABLE} (customer_id, name, issue, query_text) "
            "VALUES (%s, %s, %s, %s)",
            (customer_id, customer_name, issue, query_text),
        )
        conn.commit()
        return cursor.lastrowid
    except mysql.connector.Error as e:
        logger.warning(f"Could not save issue: {e}")
        return None


def fetch_recent_issues(limit=200):
    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT id, customer_id, name, issue, query_text, created_at "
        f"FROM {ISSUES_TABLE} ORDER BY created_at DESC LIMIT {limit}"
    )
    rows = [row_to_dict(cursor, r) for r in cursor.fetchall()]
    cursor.close()
    conn.close()
    for r in rows:
        if isinstance(r.get("created_at"), datetime):
            r["created_at"] = r["created_at"].strftime("%Y-%m-%d %H:%M:%S")
    return rows


# ── Customer field helpers ────────────────────────────────────────────────
def get_customer_name(record) -> str:
    for col in NAME_COLUMNS:
        if record.get(col):
            return str(record[col])
    return "Unknown"


def get_customer_id(record):
    for col in ID_COLUMNS:
        if record.get(col) is not None:
            return record[col]
    return None