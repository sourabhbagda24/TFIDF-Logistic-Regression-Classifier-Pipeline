import time
from flask import Blueprint, request, jsonify

from db.queries import log_classification
from ML.model import classify_with_probs
from utils.names import extract_names_from_text

classify_bp = Blueprint("classify", __name__)


@classify_bp.route("/api/classify", methods=["POST", "GET"])
def api_classify():
    t0 = time.time()
    if request.method == "GET":
        text = request.args.get("text", "").strip()
    else:
        text = request.get_json(force=True).get("text", "").strip()

    if not text:
        return jsonify({"error": "Missing 'text' field"}), 400

    result         = classify_with_probs(text)
    detected_names = extract_names_from_text(text)
    result["detected_names"] = detected_names

    response_time_ms = round((time.time() - t0) * 1000, 2)
    log_classification(
        text, result["category"], result["probability"],
        result["probabilities"], detected_names, response_time_ms,
    )

    result["response_time_ms"] = response_time_ms
    return jsonify(result)