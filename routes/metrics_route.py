from flask import Blueprint, jsonify
from ML.metrics import metrics

metrics_bp = Blueprint("metrics", __name__)


@metrics_bp.route("/api/metrics", methods=["GET"])
def api_metrics():
    return jsonify(metrics)