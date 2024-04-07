from flask import (
    Blueprint, 
    request, 
    jsonify,
    json,
    g
)
from flaskr.db import get_db
from sqlite3 import Cursor

from . import auth
from . import posts


bp = Blueprint('groups', __name__, url_prefix='/groups')

@bp.route('fetch/<groupID>', methods=['GET'])
def fetch(groupID):
    id = groupID
    if (not id):
        return jsonify({'msg', "No group id specified"}), 400

    group = get_group(id)
    if (group is None):
        return jsonify({'msg': "Group not found"}), 404

    return jsonify(dict(group)), 200


@bp.route('fetchLatestPostID/<groupID>', methods=['GET'])
def fetchLatestPostID(groupID):
    id = groupID
    if (not id):
        return jsonify({'msg', "No group id specified"}), 400

    # check for group existence
    group = get_group(id)
    if (group is None):
        return jsonify({'msg': "Group not found"}), 404
    
    # get latest post
    db = get_db()
    ret_id = db.execute('SELECT id FROM post ORDER BY created DESC LIMIT 1')

    if (ret_id is None):
        return jsonify({'msg': "Something went wrong"}), 500
    
    return jsonify(dict([_ for _ in ret_id][0])), 200


@bp.route('fetchPostRange/<groupID>', methods=['GET'])
def fetchPostRange(groupID):
    id = groupID
    start_id = request.args['start_id']
    requested_posts = request.args['requested_posts']

    if (not id):
        return jsonify({'msg', "No group id specified"}), 400
    if (not start_id):
        return jsonify({'msg', "No start post id specified"}), 400
    if (not requested_posts):
        return jsonify({'msg', "No number of requested posts specified"}), 400
        
    # check for group existence
    group = get_group(id)
    if (group is None):
        return jsonify({'msg': "Group not found"}), 404

    # check for post existence
    post = posts.get_post(start_id)
    if (post is None):
        return jsonify({'msg': "Start post not found"}), 404
    
    start_date = post['created']

    # get selected range
    db = get_db()
    ret = db.execute('SELECT id FROM post WHERE created <= ? ORDER BY created DESC', (start_date,)).fetchmany(int(requested_posts))

    return jsonify([dict(_) for _ in ret])    


@bp.route('/fetchUserGroups', methods=['GET'])
@auth.login_required
def fetchUserGroups():


    user_id = g.user['id']

    db = get_db()

    groups = db.execute(
        'SELECT * FROM userGroup WHERE user_id = ?', (user_id,)
    ).fetchall()

    return jsonify([dict(_) for _ in groups]), 200


@bp.route('/create', methods=['POST'])
@auth.login_required
def create():

    if (request.headers.get('Content-Type') == 'application/json'):
        data = request.json['username']
    else:
        data = json.loads(request.data)

    title = data['title']
    image = data['image']

    if (not title):
        return jsonify({'msg': "A title is required"}), 400
    
    db = get_db()

    image_id = None
    if (image):
        cursor: Cursor = db.execute(
            'INSERT INTO images (author_id, data_url)'
            ' VALUES (?, ?)'
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
    group_id = cursor.fetchone()

    db.commit()
    # TODO: handle errors creating userGroup
    create_userGroup(g.user['id'], group_id[0])

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
        'INSERT INTO userGroup (user_id, group_id)'
        ' VALUES (?, ?)',
        (user_id, group_id)
    )
    db.commit()

    #TODO: handle edge cases where db fails, overlap, etc
