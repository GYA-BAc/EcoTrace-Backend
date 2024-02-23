import functools

from flask import (
    Blueprint, 
    g, 
    redirect, 
    render_template, 
    request, 
    session, 
    url_for,
    Response
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db
import json


bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('POST'))
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



@bp.route('/login', methods=('POST'))
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
