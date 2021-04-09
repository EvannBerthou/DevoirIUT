import sqlite3, io, json
from typing import *
from utils import *

from flask import Blueprint, request
from werkzeug.wrappers import Response
from werkzeug.security import generate_password_hash
from flask_jwt_extended import jwt_required, get_jwt_identity

enseignants_bp = Blueprint('enseignants', __name__)

@enseignants_bp.route('/enseignant', methods=['GET'])
def get_enseignants() -> Response:
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    enseignants = c.execute("SELECT id, (nom || ' ' || prenom), mail FROM enseignant ORDER BY nom;").fetchall()
    return jsonify(enseignants)

@enseignants_bp.route('/username', methods=['GET'])
@jwt_required()
def get_username() -> Response:
    return jsonify(user = get_jwt_identity())


@enseignants_bp.route('/is_logged_in', methods=['GET'])
@jwt_required(optional=True)
def is_logged_in() -> Response:
    return jsonify('ok' if get_jwt_identity else 'not ok')

@enseignants_bp.route('/is_admin', methods=['GET'])
@jwt_required()
def get_is_admin() -> Response:
    username = get_jwt_identity()
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    r = c.execute("""
        SELECT 1 FROM enseignant
            WHERE login = ? AND admin = 1;
    """, [username]).fetchone()
    msg = 'ok' if r else 'not ok'
    return jsonify(msg)

@enseignants_bp.route('/gestion_enseignant', methods=['DELETE'])
@jwt_required()
def delete_enseignant() -> Str_response:
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    r = c.execute("DELETE FROM enseignant WHERE id = ?;", [request.args['enseignant']])
    db.commit()
    return ''

@enseignants_bp.route('/gestion_enseignant', methods=['PATCH'])
@jwt_required()
def patch_enseignant() -> Str_response:
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    mdp = generate_password_hash(request.args['mdp']) if request.args['mdp'] else None
    r = c.execute("""UPDATE enseignant SET
        nom = ?, prenom = ?, mail = ?, pwd = IFNULL(?, pwd)
        WHERE id = ?;
    """, [request.args['nom'], request.args['prenom'], request.args['mail'], mdp, request.args['id']])
    db.commit()
    return ''

@enseignants_bp.route('/gestion_enseignant', methods=['POST'])
@jwt_required()
def post_enseignant() -> Str_response:
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    pwd = generate_password_hash(request.args['mdp'])
    r = c.execute("INSERT INTO enseignant(login,nom,prenom,mail,pwd,admin) VALUES ('',?,?,?,?,0);", [
        request.args['nom'],
        request.args['prenom'],
        request.args['mail'],
        pwd])
    db.commit()
    return ''

