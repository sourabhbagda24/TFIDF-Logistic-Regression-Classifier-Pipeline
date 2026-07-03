import time
import mysql.connector
from flask import Blueprint, request, jsonify

from db.pool import get_db
from db.queries import (
    search_customers, save_issue, log_classification,
    get_customer_name, get_customer_id,
)
from ML.model import classify_with_probs
from utils.names import extract_names_from_text
# Sahi - yeh do lines karo
from utils.pii import find_pii, normalize
from config import PII_COLUMN_MAP, NAME_COLUMNS

lookup_bp = Blueprint("lookup", __name__)


@lookup_bp.route("/api/lookup", methods=["POST"])
def api_lookup():
    t0    = time.time()
    body  = request.get_json(force=True)
    query = body.get("query", "").strip()
    if not query:
        return jsonify({"error": "Empty query"}), 400

    class_result     = classify_with_probs(query)
    detected_issue   = class_result["category"]
    prediction_score = class_result["probability"]
    probabilities    = class_result["probabilities"]
    detected_names   = extract_names_from_text(query)

    try:
        conn   = get_db()
        cursor = conn.cursor()
    except mysql.connector.Error as e:
        return jsonify({
            "customers":        [],
            "issue":            detected_issue,
            "prediction_score": prediction_score,
            "probabilities":    probabilities,
            "error":            f"DB connect failed: {e}",
        }), 500

    customers, match_method, confidence = search_customers(
        cursor, query, extract_names_from_text
    )

    if not customers:
        cursor.close()
        conn.close()
        response_time_ms = round((time.time() - t0) * 1000, 2)
        log_classification(
            query, detected_issue, prediction_score,
            probabilities, detected_names, response_time_ms,
        )
        return jsonify({
            "customers":        [],
            "customer_found":   False,
            "issue":            detected_issue,
            "prediction_score": prediction_score,
            "probabilities":    probabilities,
            "query":            query,
            "detected_names":   detected_names,
            "match_method":     "none",
            "confidence":       "low",
            "saved":            False,
            "response_time_ms": response_time_ms,
            "message": (
                f"No customer found in database. "
                f"Based on your query, this appears to be a '{detected_issue}' issue "
                f"(confidence: {round(prediction_score * 100, 1)}%)."
            ),
        })

    saved_issues = []
    should_save  = confidence in ("high", "medium")
    for c in customers:
        cname  = get_customer_name(c)
        cid    = get_customer_id(c)
        row_id = save_issue(cursor, conn, cname, cid, detected_issue, query) if should_save else None
        saved_issues.append(row_id)
        c["ISSUE"] = detected_issue

    matched_by = _build_matched_by(customers, query, detected_names)

    cursor.close()
    conn.close()

    response_time_ms = round((time.time() - t0) * 1000, 2)
    log_classification(
        query, detected_issue, prediction_score,
        probabilities, detected_names, response_time_ms,
    )

    return jsonify({
        "customers":        customers,
        "customer_found":   True,
        "issue":            detected_issue,
        "prediction_score": prediction_score,
        "probabilities":    probabilities,
        "query":            query,
        "matched_by":       matched_by,
        "saved_issues":     saved_issues,
        "match_method":     match_method,
        "confidence":       confidence,
        "detected_names":   detected_names,
        "saved":            should_save,
        "response_time_ms": response_time_ms,
    })


def _build_matched_by(customers, query, detected_names) -> list:
    matched_by = []
    for c in customers:
        triggered = []
        for pii_type, col in PII_COLUMN_MAP.items():
            if col not in c:
                continue
            for item in find_pii(query):
                if item["type"] == pii_type:
                    norm   = normalize(pii_type, item["value"])
                    stored = str(c.get(col, ""))
                    if norm and norm in stored:
                        triggered.append(col)
        for name_col in NAME_COLUMNS:
            if name_col in c:
                val = str(c.get(name_col, "")).lower()
                for fn in detected_names:
                    if fn.lower() in val:
                        triggered.append(name_col)
        matched_by.append(list(set(triggered)))
    return matched_by