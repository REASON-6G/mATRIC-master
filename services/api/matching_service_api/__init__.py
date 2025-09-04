from flask import Flask, jsonify
from flask_cors import CORS
from matching_service_api.config import Config
from matching_service_api.routes.users import users_bp
from matching_service_api.routes.topics import topics_bp
from matching_service_api.routes.subscriptions import subs_bp
from matching_service_api.routes.publishers import pubs_bp
from matching_service_api.routes.metrics import metrics_bp
from matching_service_api.routes.admin import admin_bp
from matching_service_api.rabbit import rabbit_bp
from matching_service_api.match import match_bp
from matching_service_api.auth import auth_bp
from matching_service_api.utils import jwt_client, mongo_client


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config())
    CORS(app, supports_credentials=True)


    # init extensions
    jwt_client.init_app(app)
    mongo_client.init_app(app)


    # blueprints
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(topics_bp, url_prefix="/api/topics")
    app.register_blueprint(subs_bp, url_prefix="/api/subscriptions")
    app.register_blueprint(pubs_bp, url_prefix="/api/publishers")
    app.register_blueprint(metrics_bp, url_prefix="/api/metrics")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(rabbit_bp, url_prefix="/api/queues")
    app.register_blueprint(match_bp, url_prefix="/api/match")


    @app.get("/health")
    def health():
        return jsonify(status="ok"), 200


    return app