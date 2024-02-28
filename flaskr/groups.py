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

@bp.route('/fetch', methods=['GET'])
def fetch():
    id = request.json['id']
    if (not id):
        return jsonify({'msg', "No group id specified"}), 400

    group = get_group(id)
    if (group is None):
        return jsonify({'msg': "Group not found"}), 404

    return jsonify(dict(group)), 200


@bp.route('/fetchUserGroups', methods=['GET'])
def fetchUserGroups():

    username = request.json['username']

    db = get_db()

    author_id = db.execute(
        'SELECT * FROM user WHERE username = ?', (username,)
    ).fetchone()['id']

    if (not author_id):
        return jsonify({'msg': "User not found"}), 404

    groups = db.execute(
        'SELECT * FROM userGroup WHERE author_id = ?', (author_id,)
    ).fetchall()

    return jsonify([dict(_) for _ in groups]), 200


def get_group(id):
    group = get_db().execute(
        'SELECT *'
        ' FROM group g'
        ' WHERE g.id = ?',
        (id,)
    ).fetchone()

    return group