from flask import Blueprint, jsonify
from db.queries import fetch_recent_issues

issues_bp = Blueprint("issues", __name__)


@issues_bp.route("/api/issues", methods=["GET"])
def api_issues():
    try:
        rows = fetch_recent_issues(limit=200)
        return jsonify({"issues": rows})
    except Exception as e:
        return jsonify({"issues": [], "error": str(e)}), 500