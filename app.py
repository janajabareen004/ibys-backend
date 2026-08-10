import os
from flask import Flask, jsonify
from flask_cors import CORS
from routes.projects import projects_bp
from routes.progress import progress_bp
from routes.auth import auth_bp
from routes.comments import comments_bp
from routes.requests import requests_bp
from routes.images import images_bp
from routes.documents import documents_bp
from routes.meetings import meetings_bp
from routes.apartments import apartments_bp
from routes.ai_chats import ai_chats_bp
from routes.notifications import notifications_bp
from routes.tenants import tenants_bp


app = Flask(__name__)

# CORS configuration.
# If CORS_ORIGINS is set (a comma-separated list of allowed origins, e.g. the
# Lovable production domain), access is restricted to those origins. If it is
# not set, all origins are allowed (preserves the current development behavior).
# Set CORS_ORIGINS on the hosting platform to lock the API to the frontend
# domain(s) without touching code, e.g.:
#   CORS_ORIGINS=https://your-app.lovable.app,https://app.yourdomain.com
_cors_origins = os.getenv("CORS_ORIGINS")
if _cors_origins:
    _origins = [o.strip() for o in _cors_origins.split(",") if o.strip()]
    CORS(app, origins=_origins)
else:
    CORS(app)

# Register Blueprints
app.register_blueprint(projects_bp)
app.register_blueprint(progress_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(comments_bp)
app.register_blueprint(requests_bp)
app.register_blueprint(images_bp)
app.register_blueprint(documents_bp)
app.register_blueprint(meetings_bp)
app.register_blueprint(apartments_bp)
app.register_blueprint(ai_chats_bp)
app.register_blueprint(notifications_bp)
app.register_blueprint(tenants_bp)


@app.route("/")
def home():
    return jsonify({"message": "IBYS Backend is running"})


if __name__ == "__main__":
    # Local development entry point only. In production the app is served by
    # gunicorn (see Procfile: `gunicorn app:app`), which imports `app` directly
    # and never executes this block.
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "true").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)