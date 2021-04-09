import sqlite3, io, json
from typing import *
from utils import *

from flask import Blueprint, request
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.wrappers import Response

from flask_jwt_extended import (
    jwt_required, create_access_token,
    create_refresh_token,
    get_jwt_identity, set_access_cookies,
    set_refresh_cookies, unset_jwt_cookies
)

auth_bp = Blueprint('auth_bp', __name__)


@auth_bp.route('/token/auth', methods=['POST'])
def post_login() -> Response_code:
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400

    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    pass_found = c.execute('SELECT pwd FROM enseignant WHERE login = ?;', [username]).fetchone()
    if pass_found and check_password_hash(pass_found[0], password):
        # Create the tokens we will be sending back to the user
        access_token = create_access_token(identity=username, expires_delta=False)
        refresh_token = create_refresh_token(identity=username)

        # Set the JWT cookies in the response
        resp = jsonify({'login': True})
        set_access_cookies(resp, access_token)
        set_refresh_cookies(resp, refresh_token)
        return resp, 200

    return jsonify({"error": "Bad username or password"}), 401

@auth_bp.route('/token/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh() -> Response:
    # Create the new access token
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    # Set the JWT access cookie in the response
    resp = jsonify({'refresh': True})
    set_access_cookies(resp, access_token)
    return resp

@auth_bp.route('/token/remove', methods=['POST'])
def logout() -> Response:
    resp = jsonify({'logout': True})
    unset_jwt_cookies(resp)
    return resp

