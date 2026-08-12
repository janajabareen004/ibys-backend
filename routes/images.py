from flask import Blueprint, request, jsonify, g
from services.image_service import ImageService
from services.activity_service import ActivityService
from services.errors import ServiceError
from services.auth_guard import require_auth, require_roles

# This Blueprint uses full explicit paths because its routes span both
# /api/images... and /api/projects/<project_id>/images
images_bp = Blueprint("images", __name__)

image_service = ImageService()
activity_service = ActivityService()


@images_bp.route("/api/images", methods=["GET"])
def get_all_images():
    """List all images (across all projects)."""
    try:
        return jsonify(image_service.get_all()), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@images_bp.route("/api/images/<image_id>", methods=["GET"])
def get_image(image_id):
    """Get a single image by image_id."""
    try:
        return jsonify(image_service.get_by_id(image_id)), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@images_bp.route("/api/projects/<project_id>/images", methods=["GET"])
def get_project_images(project_id):
    """List all images for a single project."""
    try:
        return jsonify(image_service.get_for_project(project_id)), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@images_bp.route("/api/projects/<project_id>/images", methods=["POST"])
@require_auth
@require_roles("MANAGER", "BUILDING_COMPANY")
def create_image(project_id):
    """Create an image under a project. project_id comes only from the URL."""
    data = request.get_json(silent=True)
    try:
        created = image_service.create(project_id, data)
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status
    actor = activity_service.resolve_actor(g.current_user_id, g.current_role)
    label = created.get("title") or created.get("description") or "a photo"
    activity_service.record_event(project_id, actor, "photo_uploaded", f"uploaded {label}")
    return jsonify(created), 201


@images_bp.route("/api/images/<image_id>", methods=["PUT"])
@require_auth
@require_roles("MANAGER", "BUILDING_COMPANY")
def update_image(image_id):
    """Update an image. The id comes only from the URL."""
    data = request.get_json(silent=True)
    try:
        return jsonify(image_service.update(image_id, data)), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@images_bp.route("/api/images/<image_id>", methods=["DELETE"])
@require_auth
@require_roles("MANAGER", "BUILDING_COMPANY")
def delete_image(image_id):
    """Delete an image by image_id."""
    try:
        return jsonify(image_service.delete(image_id)), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status
