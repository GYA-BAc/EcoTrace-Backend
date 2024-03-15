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
    #TODO: user g.user['id'] if login required

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
    
    cursor: Cursor = db.execute(
        'INSERT INTO groups (title, image_id, author_id)'
        ' VALUES (?, ?, ?)'
        ' RETURNING id',
        (title, image_id, g.user['id'])
    )
    db.commit()

    group_id = cursor.fetchone()
    # TODO: handle errors creating userGroup
    create_userGroup(g.user['id'], group_id)

    return jsonify({'msg': "Success"}), 201


def get_group(id):
    group = get_db().execute(
        'SELECT *'
        ' FROM groups g'
        ' WHERE g.id = ?',
        (id,)
    ).fetchone()

    return group


def create_userGroup(user_id, group_id):

    db = get_db()
    db.execute(
        'INSERT INTO userGoup (user_id, group_id)'
        ' VALUES (?, ?)',
        (user_id, group_id)
    )
    db.commit()

    #TODO: handle edge cases where db fails, overlap, etc
