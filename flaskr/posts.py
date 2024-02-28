import functools
from flask import (
    Blueprint, 
    request, 
    jsonify,
    abort
)
from flaskr.db import get_db

from auth import login_required


bp = Blueprint('posts', __name__, url_prefix='/posts')

@bp.route('/fetch', methods=['GET'])
def fetch():
    post_id = request.json['id']
    if (not post_id):
        return jsonify({'msg', "No post id specified"}), 400

    db = get_db()

    post = db.execute(
        'SELECT * FROM post WHERE id = ?', (post_id,)
    ).fetchone()

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



@bp.route('/add', methods=['POST'])
@login_required()
def add():
    pass
    # request.json[]


def get_post(id):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if (post is None):
        return jsonify({'msg', "Post not found"}), 404
    
    return post


