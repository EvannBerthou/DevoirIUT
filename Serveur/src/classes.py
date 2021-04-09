import sqlite3, io, json
from typing import *
from utils import *

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.wrappers import Response

classes_bp = Blueprint('classes', __name__)

@classes_bp.route('/classe', methods=['GET'])
@jwt_required(optional=True)
def classes() -> Str_or_Response:
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    # Liste des classes d'un prof
    identity = get_jwt_identity()
    if identity:
        liste = c.execute("""
            SELECT nom FROM classes WHERE id IN
                (SELECT classe_id FROM classe_enseignant WHERE enseignant_id
                    = (SELECT id from enseignant WHERE login = ?));
        """, [identity]).fetchall()
        return jsonify(liste), 200

    liste = c.execute("SELECT id,nom FROM classes;").fetchall()
    return jsonify(liste), 200

@classes_bp.route('/classe_enseignant', methods=['GET'])
@jwt_required()
def classe_enseignants() -> Response:
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    ce = c.execute("""
        SELECT classes.nom, enseignant.id, (enseignant.nom || '' || enseignant.prenom)
        FROM classes, enseignant, classe_enseignant
        WHERE enseignant.id = classe_enseignant.enseignant_id
            AND classes.id = classe_enseignant.classe_id;
    """).fetchall()
    return jsonify(ce)


@classes_bp.route('/gestion_classe', methods=['DELETE'])
@jwt_required()
def delete_classe() -> Str_response:
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    r = c.execute("DELETE FROM classes WHERE id = ?;", [request.args['id']])
    db.commit()
    return ''


@classes_bp.route('/gestion_classe', methods=['PATCH'])
@jwt_required()
def patch_classe() -> Str_response:
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    c.execute("UPDATE classes SET nom = ? WHERE id = ?;", [request.args['nom'], request.args['id']])
    c.execute("DELETE FROM classe_enseignant WHERE classe_id = ?;", [request.args['id']])
    for e in request.args.getlist('enseignants'):
        c.execute("INSERT INTO classe_enseignant VALUES (?, ?);", [e, request.args['id']])
    db.commit()
    return ''


@classes_bp.route('/gestion_classe', methods=['POST'])
@jwt_required()
def post_classe() -> Str_response:
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    r = c.execute("INSERT INTO classes(nom) VALUES (?);", [request.args['name']])
    db.commit()
    return ''

