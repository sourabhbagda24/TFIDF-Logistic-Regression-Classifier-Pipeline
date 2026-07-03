import logging

# ── Database ──────────────────────────────────────────────────────────────
DB_CONFIG = {
    "host":     "localhost",
    "user":     "root",
    "password": "newpassword",
    "database": "customers_db",
}
POOL_SIZE = 10

# ── Tables ────────────────────────────────────────────────────────────────
CUSTOMERS_TABLE = "customers"
ISSUES_TABLE    = "issues"
LOG_TABLE       = "classification_log"

# ── Cache ─────────────────────────────────────────────────────────────────
LRU_MAXSIZE = 512

# ── Column mappings ───────────────────────────────────────────────────────
PII_COLUMN_MAP = {
    "PHONE":    "phone",
    "EMAIL":    "email",
    "ACCOUNT":  "account_number",
    "CARD":     "card_number",
    "AADHAAR":  "aadhaar_number",
    "PAN":      "pan_number",
    "IFSC":     "ifsc_code",
    "PIN_CODE": "pincode",
}

NAME_COLUMNS = ["name", "full_name", "customer_name"]
ID_COLUMNS   = ["id", "customer_id", "cust_id"]

# ── Non-name words (for name extraction filtering) ────────────────────────
NON_NAME_WORDS = {
    "hi", "hello", "hey", "dear", "sir", "madam", "team", "support",
    "customer", "care", "service", "agent", "representative",
    "please", "thank", "thanks", "regarding", "reaching", "attention",
    "matter", "resolution", "callback", "call", "back", "message",
    "time", "assistance", "forward", "hearing", "soon", "unable",
    "answer", "immediately", "feel", "free", "try", "again", "little",
    "later", "leave", "short", "will", "get", "possible", "look",
    "issue", "problem", "error", "payment", "refund", "delivery",
    "technical", "product", "inquiry", "order", "account", "billing",
    "discuss", "work", "toward", "whenever", "have", "some",
}

# ── Logging ───────────────────────────────────────────────────────────────
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("app.log"),
            logging.StreamHandler(),
        ],
    )

setup_logging()