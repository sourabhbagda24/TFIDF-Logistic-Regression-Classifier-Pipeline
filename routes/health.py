from datetime import datetime
from flask import Blueprint, jsonify

from db.pool import get_db
from ML.metrics import metrics
from ML.model import get_cache_info

health_bp = Blueprint("health", __name__)


@health_bp.route("/api/health", methods=["GET"])
def api_health():
    health = {
        "status":         "ok",
        "timestamp":      datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "model":          "LogisticRegression + TF-IDF",
        "accuracy":       metrics["accuracy"],
        "f1_macro":       metrics["f1_macro"],
        "cache":          "lru_memory",
        "lru_cache_info": get_cache_info(),
        "db":             "unknown",
    }
    try:
        conn = get_db()
        conn.ping(reconnect=False)
        conn.close()
        health["db"] = "ok"
    except Exception as e:
        health["db"]     = f"error: {e}"
        health["status"] = "degraded"

    return jsonify(health)