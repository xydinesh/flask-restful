from datetime import datetime
from flask import render_template, request, g, jsonify, abort, url_for
from FlaskWebTemplate import app

from FlaskWebTemplate.models import *
from flask.ext.httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username_or_token, password):
    user = User.verify_auth_token(username_or_token)
    if not user:
        user = User.query.filter_by(username = username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True

@app.route('/')
@app.route('/home')
def home():
    return render_template(
        'index.html',
        title = 'Home Page',
        year = datetime.now().year,
    )

@app.route('/api/token', methods=['POST'])
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token})

@app.route('/api/greeting', methods=['POST'])
@auth.login_required
def greeting():
    return jsonify({'greenting': 'Hello {0}'.format(g.user.username)}), 201


@app.route('/api/users', methods=['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    
    if username is None or password is None:
        abort(400)

    if User.query.filter_by(username = username).first() is not None:
        abort(400) # existing user

    user = User(username = username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({'username': user.username}), 201, {'Location': url_for('get_user', id = user.id, _external = True)}


@app.route('/api/users/<int:id>')
def get_user(id):
    user = User.query.get(id)
    if user is None:
        abort(400)
    return jsonify({'username': user.username})