from flask import (
    Blueprint, 
    request, 
    jsonify,
    g
)
from flaskr.db import get_db
from sqlite3 import Cursor

from . import auth


bp = Blueprint('posts', __name__, url_prefix='/posts')

@bp.route('/fetch', methods=['GET'])
def fetch():
    id = request.json['id']
    if (not id):
        return jsonify({'msg', "No post id specified"}), 400

    post = get_post(id)
    if (post is None):
        return jsonify({'msg', "Post not found"}), 404

    return jsonify(post), 200


@bp.route('/fetchUserPosts', methods=['GET'])
def fetchUserPosts():

    username = request.json['username']

    db = get_db()

    author_id = db.execute(
        'SELECT * FROM user WHERE username = ?', (username,)
    ).fetchone()['id']

    if (not author_id):
        return jsonify({'msg', "User not found"}), 404

    posts = db.execute(
        'SELECT * FROM post WHERE author_id = ?', (author_id,)
    ).fetchall()

    return jsonify(posts)



@bp.route('/create', methods=['POST'])
@auth.login_required
def create():
    if request.method != 'POST':
        return "Request must be POST method", 400

    title = request.json['title']
    body = request.json['body']
    image = request.json['image']

    if (not title):
        return jsonify({'msg': "A title is required"}), 400
    
    if (not body and not image):
        return jsonify({'msg': "Post body and or image required"}), 400

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
        'INSERT INTO post (title, body, image_id, author_id)'
        ' VALUES (?, ?, ?, ?)',
        (title, (body if body else None), (image_id if image else None), g.user['id'])
    )
    print((title, (body if body else None), (image_id if image else None), g.user['id']))
    db.commit()

    return jsonify({'msg': "Success"}), 201


@bp.route('/<int:id>/delete', methods=('POST',))
@auth.login_required
def delete(id):

    if (get_post(id) is None):
        return jsonify({'msg', 'Post not found'}), 404
    
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return jsonify({'msg', 'Success'}), 200


def get_post(id):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    return post



