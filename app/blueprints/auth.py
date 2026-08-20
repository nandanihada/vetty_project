from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import create_access_token

from app.errors import AuthenticationError, ValidationError

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/auth/login")
def login():
    body = request.get_json(silent=True)
    if not body:
        raise ValidationError("'username' and 'password' are required")

    username = body.get("username")
    password = body.get("password")

    if not username or not password:
        raise ValidationError("'username' and 'password' are required")

    config = current_app.config["APP_CONFIG"]

    if username != config.API_USERNAME or password != config.API_PASSWORD:
        raise AuthenticationError("Invalid username or password")

    token = create_access_token(identity=username)
    return jsonify({"access_token": token}), 200
