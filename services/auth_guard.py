from functools import wraps
from flask import request, jsonify, g
from services.auth_service import AuthService
from services.errors import ServiceError

# Reusable authentication guard.
#
# This module is ADDITIVE: it is not applied to any existing endpoint yet.
# It reuses AuthService for all token handling so the isolated-auth-client
# architecture is preserved (token validation still runs on an isolated client
# via AuthService.get_current_user, and the role lookup uses the shared
# privileged client via AuthService.get_role). No token-validation logic is
# duplicated here.

auth_service = AuthService()


def _extract_bearer_token():
    """Return the Bearer token from the Authorization header, or None.

    Requires the exact 'Bearer <token>' format.
    """
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return None
    token = header.split(" ", 1)[1].strip()
    return token or None


def require_auth(fn):
    """Decorator that authenticates the request before running the route.

    On success it populates the Flask request-context globals:
        g.current_user      -> the Supabase Auth user object
        g.current_user_id   -> the authenticated user's UUID
        g.current_role      -> the user's role from public.users (may be None)

    On failure it short-circuits with the project's standard JSON error shape:
        401 {"error": "Missing or invalid Authorization header."}  (no/invalid header)
        401 {"error": "Invalid or expired token."}                 (bad/expired token)

    It does NOT perform any role-based authorization or ownership checks; it only
    makes identity available to the decorated route.
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = _extract_bearer_token()
        if not token:
            return jsonify({"error": "Missing or invalid Authorization header."}), 401

        # Reuse AuthService's isolated-client token validation.
        user = auth_service.get_current_user(token)
        if not user:
            return jsonify({"error": "Invalid or expired token."}), 401

        try:
            role = auth_service.get_role(user.id)
        except ServiceError as e:
            return jsonify({"error": e.message}), e.status

        g.current_user = user
        g.current_user_id = user.id
        g.current_role = role

        return fn(*args, **kwargs)

    return wrapper


def require_roles(*allowed_roles):
    """Decorator that authorizes the request by role.

    MUST be applied BELOW @require_auth so that g.current_role has already been
    populated. It performs NO authentication itself: it does not read the
    Authorization header, parse/validate tokens, call Supabase, or call
    AuthService. It is a pure in-memory check that reuses g.current_role.

    Correct ordering:
        @some_bp.route(...)
        @require_auth
        @require_roles("MANAGER", "BUILDING_COMPANY")
        def handler(...):
            ...

    If the current role is not in allowed_roles (including the case where it is
    missing/None), it short-circuits with:
        403 {"error": "Forbidden: insufficient role."}
    """

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            role = getattr(g, "current_role", None)
            if role not in allowed_roles:
                return jsonify({"error": "Forbidden: insufficient role."}), 403
            return fn(*args, **kwargs)

        return wrapper

    return decorator
