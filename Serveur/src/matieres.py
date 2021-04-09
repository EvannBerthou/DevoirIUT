import sqlite3, io, json
from typing import *
from utils import *

from flask import Blueprint, request
from werkzeug.wrappers import Response

from flask_jwt_extended import jwt_required, get_jwt_identity

matieres_bp = Blueprint('matieres_bp', __name__)

@matieres_bp.route('/matieres', methods=['GET'])
@jwt_required(optional=True)
def matieres() -> Response:
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    # Liste des matieres d'un prof
    identity = get_jwt_identity()
    if identity:
        liste = c.execute("""
            SELECT nom FROM matiere WHERE id IN
                (SELECT matiere_id FROM matiere_enseignant WHERE enseignant_id
                    = (SELECT id from enseignant WHERE login = ?));
        """, [identity]).fetchall()
        return jsonify(liste)
    # Liste de toutes les matieres
    liste = c.execute("SELECT id,nom FROM matiere ORDER BY nom;").fetchall()
    return jsonify(liste)

@matieres_bp.route('/matiere_enseignant', methods=['GET'])
@jwt_required()
def get_matiere_enseignants() -> Response:
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    ce = c.execute("""
        SELECT matiere.nom, enseignant.id, (enseignant.nom || ' ' || enseignant.prenom)
        FROM matiere, enseignant, matiere_enseignant
        WHERE enseignant.id = matiere_enseignant.enseignant_id
          AND matiere.id    = matiere_enseignant.matiere_id;
    """).fetchall()
    return jsonify(ce)


@matieres_bp.route('/gestion_matieres', methods=['DELETE'])
@jwt_required()
def delete_matieres() -> Str_response:
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    r = c.execute("DELETE FROM matiere WHERE id = ?;", [request.args['id']])
    db.commit()
    return ''

@matieres_bp.route('/gestion_matieres', methods=['PATCH'])
@jwt_required()
def patch_matieres() -> Str_response:
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    c.execute("UPDATE matiere SET nom = ? WHERE id = ?;", [request.args['nom'], request.args['id']])
    c.execute("DELETE FROM matiere_enseignant WHERE matiere_id = ?;", [request.args['id']])
    for e in request.args.getlist('enseignants'):
        c.execute("INSERT INTO matiere_enseignant VALUES (?, ?);", [e, request.args['id']])
    db.commit()
    return ''

@matieres_bp.route('/gestion_matieres', methods=['POST'])
@jwt_required()
def post_matiere() -> Str_response:
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    r = c.execute("INSERT INTO matiere(nom) VALUES (?);", [request.args['name']])
    db.commit()
    return ''

