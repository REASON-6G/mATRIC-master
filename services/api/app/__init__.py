from flask import Flask, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager
from app.config import Config
from .routes.users import bp as users_bp
from .routes.topics import bp as topics_bp
from .routes.subscriptions import bp as subs_bp
from .routes.publishers import bp as pubs_bp
from .routes.metrics import bp as metrics_bp
from .routes.admin import bp as admin_bp
from app.rabbit import bp as rabbit_bp
from app.match import bp as match_bp
from app.auth import bp as auth_bp

mongo = PyMongo()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config())
    CORS(app, supports_credentials=True)


    # init extensions
    jwt.init_app(app)
    mongo.init_app(app)


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