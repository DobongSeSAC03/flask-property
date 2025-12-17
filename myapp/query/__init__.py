from flask import Blueprint

query_bp = Blueprint('query', __name__)

from . import routes
