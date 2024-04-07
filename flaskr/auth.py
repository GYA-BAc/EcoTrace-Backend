import functools
from flask import (
    Blueprint, 
    g, 
    request, 
    session, 
    jsonify,
    json
)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db


bp = Blueprint('auth', __name__, url_prefix='/auth')

# this works:
# curl --json "{\"username\":\"asdf\", \"password\":\"asdf\"}" http://127.0.0.1:5000/auth/register

# decorator to check for login
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return jsonify({'msg': "Unauthorized"}), 401

        return view(**kwargs)

    return wrapped_view



@bp.route('/register', methods=['POST'])
def register():

    if (request.headers.get('Content-Type') == 'application/json'):
        data = request.json['username']
    else:
        data = json.loads(request.data)

    username = data['username']
    password = data['password']

    db = get_db()


    if not username:
        return jsonify({'msg': 'Username Required'}), 400
    elif not password:
        return jsonify({'msg': 'Password Required'}), 400

    try:
        db.execute(
            "INSERT INTO user (username, password) VALUES (?, ?)",
            (username, generate_password_hash(password)),
        )
        db.commit()
    except db.IntegrityError:
        return jsonify({'msg': "User is already registered"}), 200
    
    return jsonify({'msg': "Created account"}), 201


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

#curl --json "{\"username\":\"asdf\", \"password\":\"asdf\"}" http://127.0.0.1:5000/auth/login
        
@bp.route('/login', methods=['POST'])
def login():

    if (request.headers.get('Content-Type') == 'application/json'):
        data = request.json['username']
    else:
        data = json.loads(request.data)

    username = data['username']
    password = data['password']

    # print(request.headers)
    
    db = get_db()
    user = db.execute(
        'SELECT * FROM user WHERE username = ?', (username,)
    ).fetchone()

    if user is None:
        return jsonify({'msg': 'Unauthorized'}), 401
    elif not check_password_hash(user['password'], password):
        return jsonify({'msg': 'Unauthorized'}), 401

    session.clear()
    session['user_id'] = user['id']
    # TODO: Add authentication sessions and tokens, maybe google?
    # NOTE: this might work if frontend has cookies

    return jsonify({'msg': 'Success'}), 200


@bp.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return jsonify({'msg': 'Success'}), 200


@bp.route('/fetchUserData', methods=['GET'])
@login_required
def fetch_user_data():
    # print(request.headers)

    # print(g.user)
    return jsonify(
        {
            'msg': 'Success',
            'content': {'id': g.user['id'], 'username': g.user['username']}
        }
    ), 200


# @bp.route('/test')
# @login_required
# def test():
#     return jsonify(session), 200