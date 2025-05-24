"""Flask server exposing the Trinity AI interface."""

from __future__ import annotations

from flask import Flask, request, jsonify

from trinity_ai import TrinityAI

app = Flask(__name__)
trinity = TrinityAI()


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


if __name__ == "__main__":  # pragma: no cover
    app.run(host="0.0.0.0", port=8000)
