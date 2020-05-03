from flask import Flask
from flask_jwt_extended import JWTManager
import os

from janaka.db import db

def create_app(test_config=None):
    #Create and configure the flask app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="Devl0pmenT",
        JWT_SECRET_KEY="devlopment@secret",
        JWT_BLACKLIST_ENABLED = True,
        JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    #Make sure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    jwt=JWTManager(app)
    @jwt.token_in_blacklist_loader
    def check_if_token_in_blacklist(decrypted_token):
        jti = decrypted_token['jti']
        stored_jti = db.revoked_tokens.find_one({'jti':jti})
        if stored_jti:
            return True
        else:
            return False

    register_blueprints(app)
    return app

def register_blueprints(app):
    from .content import content_bp
    app.register_blueprint(content_bp)
    
    from .authentication import auth_bp
    app.register_blueprint(auth_bp)