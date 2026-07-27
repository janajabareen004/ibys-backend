from flask import Blueprint, request, jsonify, g
from services.ai_chat_service import AIChatService
from services.errors import ServiceError
from services.auth_guard import require_auth, require_roles

# This Blueprint uses full explicit paths because its routes span
# /api/ai-chats... and /api/tenants/<tenant_id>/ai-chats
ai_chats_bp = Blueprint("ai_chats", __name__)

ai_chat_service = AIChatService()


@ai_chats_bp.route("/api/ai-chats", methods=["GET"])
@require_auth
def get_all_ai_chats():
    """List AI chats. A TENANT sees only its own; MANAGER/BUILDING_COMPANY see all."""
    try:
        if g.current_role == "TENANT":
            return jsonify(ai_chat_service.get_for_tenant(g.current_user_id)), 200
        return jsonify(ai_chat_service.get_all()), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@ai_chats_bp.route("/api/ai-chats/<chat_id>", methods=["GET"])
@require_auth
def get_ai_chat(chat_id):
    """Get a single AI chat. A TENANT may read only its own chat."""
    try:
        chat = ai_chat_service.get_by_id(chat_id)
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status
    if g.current_role == "TENANT" and chat.get("tenant_id") != g.current_user_id:
        return jsonify({"error": "Forbidden: you do not own this AI chat."}), 403
    return jsonify(chat), 200


@ai_chats_bp.route("/api/tenants/<tenant_id>/ai-chats", methods=["GET"])
@require_auth
def get_tenant_ai_chats(tenant_id):
    """List AI chats for a tenant. A TENANT may only query its own id."""
    if g.current_role == "TENANT" and tenant_id != g.current_user_id:
        return jsonify({"error": "Forbidden: you may only view your own AI chats."}), 403
    try:
        return jsonify(ai_chat_service.get_for_tenant(tenant_id)), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@ai_chats_bp.route("/api/ai-chats", methods=["POST"])
@require_auth
@require_roles("TENANT")
def create_ai_chat():
    """Create an AI chat record. Stores the question (and optional tenant_id);
    answer is nullable and may be filled in later. No external AI is called."""
    data = request.get_json(silent=True)
    try:
        return jsonify(ai_chat_service.create(g.current_user_id, data)), 201
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@ai_chats_bp.route("/api/ai-chats/<chat_id>", methods=["PUT"])
@require_auth
@require_roles("TENANT")
def update_ai_chat(chat_id):
    """Update an AI chat record. The id comes only from the URL."""
    data = request.get_json(silent=True)
    try:
        return jsonify(ai_chat_service.update(chat_id, data, g.current_user_id)), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@ai_chats_bp.route("/api/ai-chats/<chat_id>", methods=["DELETE"])
@require_auth
@require_roles("TENANT")
def delete_ai_chat(chat_id):
    """Delete an AI chat record by chat_id."""
    try:
        return jsonify(ai_chat_service.delete(chat_id, g.current_user_id)), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status
