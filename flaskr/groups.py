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
@auth.login_required
def fetchUserGroups():

    username = request.json['username']

    db = get_db()

    user_id = db.execute(
        'SELECT * FROM user WHERE username = ?', (username,)
    ).fetchone()['id']

    if (not user_id):
        return jsonify({'msg': "User not found"}), 404

    groups = db.execute(
        'SELECT * FROM userGroup WHERE user_id = ?', (user_id,)
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


@bp.route('/create', methods=['POST'])
@auth.login_required
def create():

    title = request.json['title']
    image = request.json['image']

    if (not title):
        return jsonify({'msg': "A title is required"}), 400
    
    db = get_db()

    image_id = None
    if (image):
        cursor: Cursor = db.execute(
            'INSERT INTO images (author_id, data_url)'
            ' VALUES (?, ?)',
            ' RETURNING id',
            (g.user['id'], image)
        )
        row = cursor.fetchone()

        if (row is None):
            return jsonify({'msg', "Failed saving image"}), 501
        
        (image_id, ) = row
    
    db.execute(
        'INSERT INTO group (title, image_id, author_id)'
        ' VALUES (?, ?, ?)',
        (title, image_id, g.user['id'])
    )
    # print((title, (image_id if image else None), g.user['id']))
    db.commit()

    return jsonify({'msg': "Success"}), 201