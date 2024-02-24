import functools
from flask import (
    Blueprint, 
    g, 
    request, 
    session, 
)
from flaskr.db import get_db


bp = Blueprint('posts', __name__, url_prefix='/posts')

@bp.route('/query', methods=['GET'])
def query():
    pass