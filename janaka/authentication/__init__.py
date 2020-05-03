from flask import Blueprint
from flask_restful import Api

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
auth_api = Api(auth_bp)

from . import auth_routes