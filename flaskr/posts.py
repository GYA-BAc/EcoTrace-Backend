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
from . import groups


bp = Blueprint('posts', __name__, url_prefix='/posts')

@bp.route('fetch/<postID>', methods=['GET'])
def fetch(postID):
    id = postID
    if (not id):
        return jsonify({'msg', "No post id specified"}), 400

    post = get_post(id)
    if (post is None):
        return jsonify({'msg': "Post not found"}), 404

    return jsonify(post), 200


@bp.route('/fetchUserPosts/<authorID>', methods=['GET'])
def fetchUserPosts(authorID):

    author_id = authorID

    db = get_db()

    if (not author_id):
        return jsonify({'msg': "ID needed"}), 404

    posts = db.execute(
        'SELECT * FROM post WHERE author_id = ?', (author_id,)
    ).fetchall()

    return jsonify([dict(_) for _ in posts]), 200



@bp.route('/create', methods=['POST'])
@auth.login_required
def create():

    if (request.headers.get('Content-Type') == 'application/json'):
        data = request.json
    else:
        data = json.loads(request.data)

    body = data['body']
    image = data['image']
    group_id = data['group_id']
    location = data['location']

    print(location)
    
    if (not body and not image):
        return jsonify({'msg': "Post body and or image required"}), 400
    
    if (not group_id):
        return jsonify({'msg': "Post must be in a group"}), 400
    
    if (not location):
        return jsonify({'msg': "Location data needed to create post"}), 400

    db = get_db()

    # check if group exists
    if (groups.get_group(group_id) is None):
        return jsonify({'msg': "Invalid group"}), 400
    

    image_id = None
    if (image):
        row = db.execute(
            'INSERT INTO images (author_id, data_url)'
            ' VALUES (?, ?)'
            ' RETURNING id',
            (g.user['id'], image)
        ).fetchone()

        if (row is None):
            return jsonify({'msg', "Failed saving image"}), 501
        
        (image_id, ) = row
    
    post_id = None
    row = db.execute(
        'INSERT INTO post (body, image_id, group_id, author_id)'
        ' VALUES (?, ?, ?, ?)'
        ' RETURNING id',
        ((body if body else None), (image_id if image else None), group_id, g.user['id'])
    ).fetchone()

    if (row is None):
        return jsonify({'msg': "Failed saving post"})
    
    (post_id, ) = row
    
    # insert location
    db.execute(
        'INSERT INTO locations (latitude, longitude, post_id)'
        ' VALUES (?, ?, ?)',
        (location['latitude'], location['longitude'], post_id)
    )

    # print(((body if body else None), (image_id if image else None), g.user['id']))
    db.commit()

    return jsonify({'msg': "Success"}), 201


@bp.route('/delete', methods=('POST',))
@auth.login_required
def delete():

    if (request.headers.get('Content-Type') == 'application/json'):
        data = request.json
    else:
        data = json.loads(request.data)

    # add temp perms check
    if (data['key'] != 'SECRET'):
        return jsonify({'msg': 'Unauthorized'}), 401

    id = data['id']

    if (get_post(id) is None):
        return jsonify({'msg': 'Post not found'}), 404
    
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return jsonify({'msg': 'Success'}), 200


def get_post(id) -> dict:
    db = get_db()

    post = db.execute(
        'SELECT *'
        ' FROM post p'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if (post is None):
        return None

    # populate username 
    username = db.execute(
        'SELECT username'
        ' FROM user u'
        ' WHERE u.id = ?',
        (post['author_id'], )
    ).fetchone()

    # populate image
    # NOTE: this could be a security vulnerability
    data_url = db.execute(
        'SELECT data_url'
        ' FROM images i'
        ' WHERE i.id = ?',
        (post['image_id'], )
    ).fetchone()

    #TODO ensure post's user exist

    return {
        'id': post['id'],
        'group_id': post['group_id'],
        'created': post['created'],
        'username': username[0],
        'body': post['body'],
        'data_url': data_url[0],
    }



