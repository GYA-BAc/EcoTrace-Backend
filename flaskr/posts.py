from flask import (
    Blueprint, 
    request, 
    jsonify,
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

    return jsonify(dict(post)), 200


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

    body = request.json['body']
    image = request.json['image']
    group_id = request.json['group_id']

    
    if (not body and not image):
        return jsonify({'msg': "Post body and or image required"}), 400
    
    if (not group_id):
        return jsonify({'msg': "Post must be in a group"}), 400

    db = get_db()

    # check if group exists
    if (groups.get_group(group_id) is None):
        return jsonify({'msg': "Invalid group"}), 400
    

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
    
    db.execute(
        'INSERT INTO post (body, image_id, group_id, author_id)'
        ' VALUES (?, ?, ?, ?)',
        ((body if body else None), (image_id if image else None), group_id, g.user['id'])
    )
    # print(((body if body else None), (image_id if image else None), g.user['id']))
    db.commit()

    return jsonify({'msg': "Success"}), 201


@bp.route('/delete', methods=('POST',))
@auth.login_required
def delete():
    id = request.json['id']

    if (get_post(id) is None):
        return jsonify({'msg': 'Post not found'}), 404
    
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return jsonify({'msg': 'Success'}), 200


def get_post(id):
    post = get_db().execute(
        'SELECT *'
        ' FROM post p'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    #TODO ensure post's user exist

    return post



