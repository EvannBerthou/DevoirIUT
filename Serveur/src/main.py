import sqlite3
from flask import Flask, request, jsonify
from api import api
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
from werkzeug.security import generate_password_hash, check_password_hash, safe_str_cmp

app = Flask(__name__)
app.register_blueprint(api, url_prefix='/api')
app.secret_key = 'secret key'
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!
jwt = JWTManager(app)

@app.route('/login', methods=['POST'])
def login():
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
    pass_found = c.execute('SELECT id, mail, pwd FROM enseignant WHERE mail = ?;', [username]).fetchone()
    if pass_found and check_password_hash(pass_found[2], password):
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    return jsonify({"error": "Bad username or password"}), 401

@app.route('/protected', methods=['GET'])
@jwt_required
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200
