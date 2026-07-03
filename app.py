import time
import logging
from flask import Flask, g, request

from config import DB_CONFIG, POOL_SIZE
from db.queries import init_db
from ML.metrics import metrics
from routes.lookup import lookup_bp
from routes.classify import classify_bp
from routes.metrics_route import metrics_bp
from routes.issues import issues_bp
from routes.health import health_bp

logger = logging.getLogger(__name__)

app = Flask(__name__)

# ── Register blueprints ───────────────────────────────────────────────────
app.register_blueprint(lookup_bp)
app.register_blueprint(classify_bp)
app.register_blueprint(metrics_bp)
app.register_blueprint(issues_bp)
app.register_blueprint(health_bp)

# ── Request timing middleware ─────────────────────────────────────────────
@app.before_request
def start_timer():
    g.start_time = time.time()

@app.after_request
def log_request(response):
    duration_ms = round((time.time() - g.start_time) * 1000, 2)
    logger.info(f"{request.method} {request.path} → {response.status_code} ({duration_ms}ms)")
    response.headers["X-Response-Time-Ms"] = str(duration_ms)
    return response

# ── Startup ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    print("=" * 55)
    print("  Customer Lookup REST API")
    print("=" * 55)
    print(f"  DB Pool : {POOL_SIZE} connections @ {DB_CONFIG['host']}")
    print(f"  Cache   : In-memory LRU")
    print(f"  Model   : Logistic Regression | Accuracy: {metrics['accuracy']}")
    print(f"  F1      : {metrics['f1_macro']}")
    print()
    print("  Endpoints:")
    print("  POST http://localhost:5000/api/lookup")
    print("  POST http://localhost:5000/api/classify")
    print("  GET  http://localhost:5000/api/metrics")
    print("  GET  http://localhost:5000/api/issues")
    print("  GET  http://localhost:5000/api/health")
    print("=" * 55)
    app.run(debug=True, host="0.0.0.0", port=5000)