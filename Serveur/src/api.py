import sqlite3, io, json
from typing import *

from flask import Blueprint, request, send_from_directory, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.wrappers import Response

from flask_jwt_extended import (
    jwt_required, create_access_token, jwt_optional,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity, set_access_cookies,
    set_refresh_cookies, unset_jwt_cookies
)

api = Blueprint('api', __name__)

Str_response = str
Str_code = Tuple[str, int]
Str_or_Response = Tuple[Union[str, Response], int]
Response_code = Tuple[Response, int]

def safe_name(name: str) -> str:
    keep = (' ','.','_')
    return "".join(c for c in name if c.isalnum() or c in keep).rstrip()

# Reécriture du jsonify de Flask afin d'avoir Response en type
def jsonify(*args: Any, **kwargs: Any) -> Response:
    if args and kwargs:
        raise TypeError("jsonify() behavior undefined when passed both args and kwargs")
    elif len(args) == 1:  # single args are passed directly to dumps()
        data = args[0]
    else:
        data = args or kwargs
    data = f"{json.dumps(data)}\n"
    return Response(data, mimetype='application/json')

def devoir_classe(classe: str) -> List[str]:
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    return c.execute("""
        SELECT * FROM (
            SELECT
                devoirs.id as did, enonce, matiere, prof, jour, null, null,
                REPLACE(REPLACE(a_rendre, 0, 'Non'), 1, 'Oui')
            FROM
                devoirs
            WHERE
                devoirs.id NOT IN (SELECT devoir_id FROM devoir_pj)
            UNION
            SELECT
                devoirs.id as did, enonce, matiere, prof, jour, pj.id, pj.nom,
                REPLACE(REPLACE(a_rendre, 0, 'Non'), 1, 'Oui')
            FROM
                devoirs, pj, devoir_pj
            WHERE
                devoir_pj.devoir_id = devoirs.id AND devoir_pj.pj_id = pj.id
        )
        WHERE (
            did IN (SELECT devoir_id FROM devoir_classe, classes WHERE classe_id = classes.id AND classes.nom = ?)
            AND jour >= DATE('now')
        );
    """,
    [classe]).fetchall()

def devoir_enseignant(username: str) -> List[str]:
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    return c.execute("""
        SELECT *
        FROM (
            SELECT
                devoirs.id as did, enonce, matiere, prof, jour, null, null,
                REPLACE(REPLACE(a_rendre, 0, 'Non'), 1, 'Oui')
            FROM
                devoirs
            WHERE
                devoirs.id NOT IN (SELECT devoir_id FROM devoir_pj)
            UNION
            SELECT
                devoirs.id as did, enonce, matiere, prof, jour, pj.id, pj.nom,
                REPLACE(REPLACE(a_rendre, 0, 'Non'), 1, 'Oui')
            FROM
                devoirs, pj, devoir_pj
            WHERE
                devoir_pj.devoir_id = devoirs.id AND devoir_pj.pj_id = pj.id
       )
       WHERE prof = ?;
    """,
    [username]).fetchall()

def get_class(id_devoir: int) -> List[str]:
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    return c.execute("""
        SELECT nom
        FROM classes
        WHERE id IN (SELECT classe_id
                     FROM devoir_classe
                     WHERE devoir_id=? );
        """,
        [id_devoir]).fetchall()

# Fusionne les colonnes afin d'avoir les pièces jointes dans une liste
def merge_pj(devoirs: List, prof: bool = False) -> List:
    parsed = {}
    for row in devoirs:
        devoir_id = row[0]
        if not devoir_id in parsed: # Si c'est la première fois qu'on rencontre un devoir avec cet id
            parsed[devoir_id] = list(row[0:5]) + [[]] + list(row[7:]) + [[classe[0] for classe in get_class(devoir_id) if prof]]
        # S'il y a une pièce jointe
        if row[5]:
            parsed[devoir_id][5].append((str(row[5]), row[6]))
    return list(parsed.values())

"""
DEVOIRS
"""

@api.route('/devoirs', methods=['POST'])
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

@api.route('/devoirs', methods=['GET'])
@jwt_optional
def get_devoirs() -> Response_code:
    username = get_jwt_identity()
    if not username:
        if 'classe' in request.args:
            devoirs = merge_pj(devoir_classe(request.args['classe']))
            return jsonify(devoirs=devoirs), 200
        return Response(), 401

    devoirs = merge_pj(devoir_enseignant(username))
    return jsonify(user=username, devoirs=devoirs), 200


@api.route('/sup',methods=['POST'])
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

@api.route('/pj', methods=['GET'])
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

@api.route('/modif', methods=['PUT'])
def put_devoir() -> Str_response:
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    f = c.execute("UPDATE devoirs SET enonce=?, jour=? WHERE id=?", [request.args['enonce'], request.args['date'], request.args['devoir_id']])
    db.commit()
    return ''
"""
Classe
"""

@api.route('/classe', methods=['GET'])
@jwt_optional
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

@api.route('/classe_enseignant', methods=['GET'])
@jwt_required
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


@api.route('/gestion_classe', methods=['DELETE'])
@jwt_required
def delete_classe() -> Str_response:
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    r = c.execute("DELETE FROM classes WHERE id = ?;", [request.args['id']])
    db.commit()
    return ''


@api.route('/gestion_classe', methods=['PATCH'])
@jwt_required
def patch_classe() -> Str_response:
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    c.execute("UPDATE classes SET nom = ? WHERE id = ?;", [request.args['nom'], request.args['id']])
    c.execute("DELETE FROM classe_enseignant WHERE classe_id = ?;", [request.args['id']])
    for e in request.args.getlist('enseignants'):
        c.execute("INSERT INTO classe_enseignant VALUES (?, ?);", [e, request.args['id']])
    db.commit()
    return ''


@api.route('/gestion_classe', methods=['POST'])
@jwt_required
def post_classe() -> Str_response:
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    r = c.execute("INSERT INTO classes(nom) VALUES (?);", [request.args['name']])
    db.commit()
    return ''


"""
Enseignants
"""

@api.route('/enseignant', methods=['GET'])
def get_enseignants() -> Response:
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    enseignants = c.execute("SELECT id, (nom || ' ' || prenom), mail FROM enseignant ORDER BY nom;").fetchall()
    return jsonify(enseignants)

@api.route('/username', methods=['GET'])
@jwt_required
def get_username() -> Response:
    return jsonify(user = get_jwt_identity())


@api.route('/is_logged_in', methods=['GET'])
@jwt_optional
def is_logged_in() -> Response:
    return jsonify('ok' if get_jwt_identity else 'not ok')

@api.route('/is_admin', methods=['GET'])
@jwt_required
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

@api.route('/gestion_enseignant', methods=['DELETE'])
@jwt_required
def delete_enseignant() -> Str_response:
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    r = c.execute("DELETE FROM enseignant WHERE id = ?;", [request.args['enseignant']])
    db.commit()
    return ''

@api.route('/gestion_enseignant', methods=['PATCH'])
@jwt_required
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

@api.route('/gestion_enseignant', methods=['POST'])
@jwt_required
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

"""
Matières
"""

@api.route('/matieres', methods=['GET'])
@jwt_optional
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

@api.route('/matiere_enseignant', methods=['GET'])
@jwt_required
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


@api.route('/gestion_matieres', methods=['DELETE'])
@jwt_required
def delete_matieres() -> Str_response:
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    r = c.execute("DELETE FROM matiere WHERE id = ?;", [request.args['id']])
    db.commit()
    return ''

@api.route('/gestion_matieres', methods=['PATCH'])
@jwt_required
def patch_matieres() -> Str_response:
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    c.execute("UPDATE matiere SET nom = ? WHERE id = ?;", [request.args['nom'], request.args['id']])
    c.execute("DELETE FROM matiere_enseignant WHERE matiere_id = ?;", [request.args['id']])
    for e in request.args.getlist('enseignants'):
        c.execute("INSERT INTO matiere_enseignant VALUES (?, ?);", [e, request.args['id']])
    db.commit()
    return ''

@api.route('/gestion_matieres', methods=['POST'])
@jwt_required
def post_matiere() -> Str_response:
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    r = c.execute("INSERT INTO matiere(nom) VALUES (?);", [request.args['name']])
    db.commit()
    return ''

"""
AUTH JWT
"""

@api.route('/token/auth', methods=['POST'])
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

@api.route('/token/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh() -> Response:
    # Create the new access token
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    # Set the JWT access cookie in the response
    resp = jsonify({'refresh': True})
    set_access_cookies(resp, access_token)
    return resp

@api.route('/token/remove', methods=['POST'])
def logout() -> Response:
    resp = jsonify({'logout': True})
    unset_jwt_cookies(resp)
    return resp

