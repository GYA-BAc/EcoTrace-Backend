import functools
from flask import (
    Blueprint, 
    g, 
    request, 
    session, 
)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db


bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['POST'])
def register():
    if request.method != 'POST':
        return "Request must be POST method", 400

    username = request.form['username']
    password = request.form['password']
    db = get_db()


    if not username:
        return 'Username Required', 400
    elif not password:
        return 'Password Required', 400

    try:
        db.execute(
            "INSERT INTO user (username, password) VALUES (?, ?)",
            (username, generate_password_hash(password)),
        )
        db.commit()
    except db.IntegrityError:
        return f"User {username} is already registered", 200
    
    return "Created account", 201


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/login', methods=['POST'])
def login():
    if request.method != 'POST':
        return "Request must be POST method", 400
    
    username = request.form['username']
    password = request.form['password']
    db = get_db()
    user = db.execute(
        'SELECT * FROM user WHERE username = ?', (username,)
    ).fetchone()

    if user is None:
        return 'Incorrect username', 401
    elif not check_password_hash(user['password'], password):
        return 'Incorrect password', 401

    session.clear()
    session['user_id'] = user['id']

    return 'Success', 200


@bp.route('/logout')
def logout():
    session.clear()
    return 'Success', 200


# decorator to check for login
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return "Unauthorized", 401

        return view(**kwargs)

    return wrapped_view