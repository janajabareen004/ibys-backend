from flask import Blueprint, request, jsonify
from services.auth_service import AuthService
from services.errors import ServiceError

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

auth_service = AuthService()


def _get_bearer_token():
    """Return the Bearer token from the Authorization header, or None."""
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return None
    token = header.split(" ", 1)[1].strip()
    return token or None


@auth_bp.route("/register", methods=["POST"])
def register():
    """Create the Auth user, the public.users row, and the role-specific row."""
    data = request.get_json(silent=True)
    try:
        return jsonify(auth_service.register(data)), 201
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@auth_bp.route("/login", methods=["POST"])
def login():
    """Sign the user in and return session tokens plus the user's role."""
    data = request.get_json(silent=True)
    try:
        return jsonify(auth_service.login(data)), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """Revoke the current session."""
    token = _get_bearer_token()
    if not token:
        return jsonify({"error": "Missing or invalid Authorization header."}), 401
    try:
        return jsonify(auth_service.logout(token)), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@auth_bp.route("/me", methods=["GET"])
def me():
    """Return the authenticated user's public profile, role, and role-specific profile."""
    token = _get_bearer_token()
    if not token:
        return jsonify({"error": "Missing or invalid Authorization header."}), 401
    try:
        return jsonify(auth_service.get_me(token)), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status
