from flask import (
    Blueprint, 
    request, 
    jsonify,
    g
)
from flaskr.db import get_db
from sqlite3 import Cursor

from . import auth


bp = Blueprint('groups', __name__, url_prefix='/groups')





def get_group(id):
    group = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username, image_id'
        ' FROM group p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    return group