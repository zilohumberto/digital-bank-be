from flask import request, jsonify, g
from functools import wraps

from application.services.auth_service import AuthService

auth_service = AuthService()


def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('X-Auth-Token')
        if not token:
            return jsonify({"status": "failure", "message": "Token is missing!"}), 401

        user = auth_service.validate_token(token)
        if user is None:
            return jsonify({"status": "failure", "message": "Invalid token!"}), 403

        # logged user
        g.user_id = user["id"]
        g.profile = user["profile"]
        return f(*args, **kwargs)
    return decorated_function
