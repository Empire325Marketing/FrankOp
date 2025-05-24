"""Flask server exposing the Trinity AI interface."""

from __future__ import annotations

from flask import Flask, request, jsonify
import os
from flask_cors import CORS

from trinity_ai import TrinityAI

app = Flask(__name__)
CORS(app)
trinity = TrinityAI()
PINARCH_TOKEN = os.getenv("PINARCH_TOKEN", "DSFSfdss22$24@21--sdfsfsdf2442442")


@app.route("/api/chat", methods=["POST"])
def chat() -> tuple:
    """Return a chat completion from the selected model."""
    data = request.get_json(force=True)
    prompt = data.get("prompt")
    model = data.get("model", "openai")
    if not prompt:
        return jsonify({"error": "prompt required"}), 400
    try:
        response = trinity.chat(prompt, model=model)
    except Exception as exc:  # pragma: no cover - network failures
        return jsonify({"error": str(exc)}), 500
    return jsonify({"response": response})


@app.route("/api/login", methods=["POST"])
def login() -> tuple:
    """Authenticate using the Pinarch token."""
    data = request.get_json(force=True)
    token = data.get("token")
    if token == PINARCH_TOKEN:
        return jsonify({"success": True})
    return jsonify({"success": False}), 401


@app.route("/api/status", methods=["GET"])
def status() -> tuple:
    """Simple status endpoint for health checks."""
    return jsonify({"status": "ok"})


@app.route("/health", methods=["GET"])
def health() -> tuple:
    """Compatibility health check endpoint."""
    return jsonify({"status": "healthy"})


if __name__ == "__main__":  # pragma: no cover
    app.run(host="0.0.0.0", port=8000)
