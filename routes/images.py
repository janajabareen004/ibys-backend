from flask import Blueprint, request, jsonify
from services.image_service import ImageService
from services.errors import ServiceError
from services.auth_guard import require_auth, require_roles

# This Blueprint uses full explicit paths because its routes span both
# /api/images... and /api/projects/<project_id>/images
images_bp = Blueprint("images", __name__)

image_service = ImageService()


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
        return jsonify(image_service.create(project_id, data)), 201
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


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
