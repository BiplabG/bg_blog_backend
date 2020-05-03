from flask import(
    Blueprint
)
from flask_restful import Api

#Declare the content blueprint
content_bp = Blueprint('content', __name__, url_prefix='/')
#Initialize the flask_restful api for content_bp
content_api = Api(content_bp)
from . import blog_routes
from . import section_routes
from . import series_routes
from . import overview_routes