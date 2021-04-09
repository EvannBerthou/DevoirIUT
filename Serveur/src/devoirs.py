import sqlite3, io, json
from typing import *
from utils import *

from flask import Blueprint, request, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.wrappers import Response

devoirs_bp = Blueprint('devoirs', __name__)

@devoirs_bp.route('/devoirs', methods=['POST'])
@jwt_required
def post_devoir() -> Str_response:
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    enonce = request.args['enonce']
    matiere = request.args['matiere']
    prof = get_jwt_identity()
    date = request.args['date']

    # Récupère le nom et le contenue des fichiers ssi il y a des fichiers
    pjs = [(fn, f.stream.read()) for fn, f in request.files.items() if fn != '']

    pj_ids = []
    for filename, blob in pjs:
        c.execute("INSERT INTO pj (nom, contenue) VALUES (?, ?);", [filename, blob])
        pj_ids.append(c.execute("SELECT id FROM pj WHERE id=(SELECT MAX(id) FROM pj);").fetchone()[0])

    c.execute("""
        INSERT INTO devoirs (enonce,matiere,prof,jour) VALUES (?, ?, ?,
            IFNULL(?, (date(datetime('now', '+7 day', 'localtime')))));
    """,
    [enonce,matiere,prof,date])

    devoir_id = c.execute("SELECT id FROM devoirs WHERE id=(SELECT MAX(id) FROM devoirs);").fetchone()[0]
    for classe in request.args['classe'].split(','):
        c.execute("""
            INSERT INTO devoir_classe
            VALUES (?, (SELECT id FROM classes WHERE nom = ?));
        """,
        [devoir_id, classe])

    for pj_id in pj_ids:
        c.execute("INSERT INTO devoir_pj (devoir_id, pj_id) VALUES (?, ?);", [devoir_id, pj_id])

    db.commit()
    return ''

@devoirs_bp.route('/devoirs', methods=['GET'])
@jwt_required(optional=True)
def get_devoirs() -> Response_code:
    username = get_jwt_identity()
    if not username:
        if 'classe' in request.args:
            devoirs = merge_pj(devoir_classe(request.args['classe']))
            return jsonify(devoirs=devoirs), 200
        return Response(), 401

    devoirs = merge_pj(devoir_enseignant(username))
    return jsonify(user=username, devoirs=devoirs), 200


@devoirs_bp.route('/sup',methods=['POST'])
def sup_devoir() -> Str_response:
    db = sqlite3.connect('src/devoirs.db')
    i = request.args['devoir_id']
    c = db.cursor()
    c.execute("DELETE FROM pj WHERE devoir_id = ?;", [i])
    c.execute("DELETE FROM devoir_pj WHERE devoir_id = ?;", [i])
    c.execute("DELETE FROM devoir_classe WHERE devoir_id = ?;", [i])
    c.execute("DELETE FROM devoirs WHERE id = ?;", [i])
    db.commit()
    return ''

@devoirs_bp.route('/pj', methods=['GET'])
def pj() -> Str_or_Response:
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    f = c.execute("SELECT nom, contenue FROM pj WHERE id = ?;", [request.args['id']]).fetchone()
    # Si aucun fichier n'a été trouvé dans la base de donné
    if f == None:
        # Message d'erreur
        return '', 404

    # io.BytesIO permet de créer une sorte de fichier mais uniquement dans la RAM (au lieu d'écrire
    # dans un fichier puis de le lire comme on faisait avant, cela permet un gain de performance
    # énorme car cela évite de devoir faire un écrire puis lecture du fichier sur le disque dur
    return send_file(io.BytesIO(f[1]), as_attachment=True, attachment_filename=safe_name(f[0])), 200

@devoirs_bp.route('/modif', methods=['PUT'])
def put_devoir() -> Str_response:
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    f = c.execute("UPDATE devoirs SET enonce=?, jour=? WHERE id=?", [request.args['enonce'], request.args['date'], request.args['devoir_id']])
    db.commit()
    return ''
