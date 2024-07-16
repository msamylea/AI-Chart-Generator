from fastapi import HTTPException
from openai import AuthenticationError, RateLimitError, BadRequestError
from flask import jsonify

def handle_llm_error(e: Exception) -> HTTPException:
    if isinstance(e, AuthenticationError):
        return jsonify({"error": "Authentication failed. Please check your API key."}), 401
    elif isinstance(e, RateLimitError):
        return jsonify({"error": "Rate limit exceeded. Please try again later."}), 429
    elif isinstance(e, BadRequestError):
        return jsonify({"error": f"Bad request: {str(e)}"}), 400
    else:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
