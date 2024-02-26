import functools
from flask import (
    Blueprint, 
    request, 
)
from flaskr.db import get_db

from auth import login_required


bp = Blueprint('posts', __name__, url_prefix='/posts')

@bp.route('/query', methods=['GET'])
def query():
    post_id = request.json['id']
    

@bp.route('/query', methods=['GET'])
def user():
    username = request.json['username']
    selection = request.json['selection']




@bp.route('/add', methods=['POST'])
@login_required()
def add():
    pass
    # request.json[]