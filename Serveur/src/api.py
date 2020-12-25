import sqlite3, os, io
from flask import Blueprint, request, jsonify, send_from_directory, send_file
from werkzeug.security import generate_password_hash, check_password_hash

from flask_jwt_extended import (
    jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity, set_access_cookies,
    set_refresh_cookies, unset_jwt_cookies
)

api = Blueprint('api', __name__)

def safe_name(name):
    keep = (' ','.','_')
    return "".join(c for c in name if c.isalnum() or c in keep).rstrip()

def ajouter_devoir(args, files):
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    enonce, matiere, prof = args["enonce"], args["matiere"], args["prof"]
    date = args['date'] if args['date'] else None

    # Récupère le nom et le contenue des fichiers ssi il y a des fichiers
    pjs = [(fn, f.stream.read()) for fn, f in files.items() if fn != '']

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

    for classe in args.getlist('classe'):
        c.execute("""
            INSERT INTO devoir_classe
            VALUES (?, (SELECT id FROM classes WHERE nom = ?));
        """,
        [devoir_id, classe])

    for pj_id in pj_ids:
        c.execute("INSERT INTO devoir_pj (devoir_id, pj_id) VALUES (?, ?);", [devoir_id, pj_id])

    db.commit()
    return jsonify({}), 200

def liste_devoirs(args):
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    parsed = {}
    if 'classe' in args:
        devoirs = c.execute("""
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
            WHERE
               did IN (SELECT devoir_id FROM devoir_classe, classes
                              WHERE classe_id = classes.id AND classes.nom = ?);
        """,
        [args['classe']]).fetchall()

        # Fusionne les colonnes afin d'avoir les pièces jointes dans une liste

        for row in devoirs:
            devoir_id = row[0]
            if not devoir_id in parsed: # Si c'est la première fois qu'on rencontre un devoir avec cet id
                parsed[devoir_id] = list(row[1:5]) + [[]] + list(row[7:])
            # S'il y a une pièce jointe
            if row[5]:
                parsed[devoir_id][4].append((str(row[5]), row[6]))

    elif 'user' in args:
        devoirs = c.execute("""
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
           WHERE
               matiere IN (SELECT nom
                           FROM matiere
                           WHERE id
                           IN (SELECT matiere_id
                               FROM matiere_enseignant, enseignant
                               WHERE enseignant_id = enseignant.id AND mail = ?)
               );
        """,
        [args['user']]).fetchall()
        for row in devoirs:
            parsed[row[0]] = list(row[:5]) + [[]] + list(row[7:])
            # S'il y a une pièce jointe

            if row[5]:
                parsed[row[0]][5].append((row[5], row[6]))

    return jsonify(list(parsed.values())), 200


@api.route('/sup',methods=['POST'])
def sup_devoir():
    db = sqlite3.connect('src/devoirs.db')
    i = request.args['devoir_id']
    c = db.cursor()
    c.execute("DELETE FROM pj WHERE devoir_id = ?;", [i])
    c.execute("DELETE FROM devoir_pj WHERE devoir_id = ?;", [i])
    c.execute("DELETE FROM devoir_classe WHERE devoir_id = ?;", [i])
    c.execute("DELETE FROM devoirs WHERE id = ?;", [i])
    db.commit()
    return '', 200

@api.route('/token/auth', methods=['POST'])
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
        # Create the tokens we will be sending back to the user
        access_token = create_access_token(identity=username)
        refresh_token = create_refresh_token(identity=username)

        # Set the JWT cookies in the response
        resp = jsonify({'login': True})
        set_access_cookies(resp, access_token)
        set_refresh_cookies(resp, refresh_token)
        return resp, 200

    return jsonify({"error": "Bad username or password"}), 401

# Same thing as login here, except we are only setting a new cookie
# for the access token.
@api.route('/token/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    # Create the new access token
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)

    # Set the JWT access cookie in the response
    resp = jsonify({'refresh': True})
    set_access_cookies(resp, access_token)
    return resp, 200

# Because the JWTs are stored in an httponly cookie now, we cannot
# log the user out by simply deleting the cookie in the frontend.
# We need the backend to send us a response to delete the cookies
# in order to logout. unset_jwt_cookies is a helper function to
# do just that.
@api.route('/token/remove', methods=['POST'])
def logout():
    resp = jsonify({'logout': True})
    unset_jwt_cookies(resp)
    return resp, 200

@api.route('/user', methods=['GET'])
def user():
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    email = request.args['email']
    user_found = c.execute('SELECT 1 FROM enseignant WHERE mail = ?', [email]).fetchone()
    return '', 404 if user_found == None else 200

@api.route('/devoirs', methods=['GET'])
def get_devoirs():
    return liste_devoirs(request.args)

@api.route('/devoirs', methods=['POST'])
def post_devoirs():
    return ajouter_devoir(request.args, request.files)


@api.route('/classe', methods=['GET'])
def classes():
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    classes = c.execute("SELECT nom FROM classes;").fetchall()
    return jsonify(classes), 200

@api.route('/matieres', methods=['GET'])
def matieres():
    print('t')
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    enseignant = request.args['enseignant']
    if not enseignant:
        return None, 404

    matieres = c.execute("""
        SELECT nom FROM matiere
        WHERE id IN
            (SELECT matiere_id FROM matiere_enseignant
                WHERE enseignant_id = ?);
    """,
    [enseignant]).fetchall()
    return jsonify(matieres), 200

@api.route('/pj', methods=['GET'])
def pj():
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    f = c.execute("SELECT nom, contenue FROM pj WHERE id = ?;", [request.args['id']]).fetchone()
    # Si aucun fichier n'a été trouvé dans la base de donné
    if f == None:
        # Message d'erreur
        return None, 404

    # io.BytesIO permet de créer une sorte de fichier mais uniquement dans la RAM (au lieu d'écrire
    # dans un fichier puis de le lire comme on faisait avant, cela permet un gain de performance
    # énorme car cela évite de devoir faire un écrire puis lecture du fichier sur le disque dur
    res = send_file(io.BytesIO(f[1]), as_attachment=True, attachment_filename=safe_name(f[0]))
    return res, 200

@api.route('/modif', methods=['PUT'])
def modif():
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    f = c.execute("UPDATE devoirs SET enonce=?, jour=? WHERE id=?", [request.args['enonce'], request.args['date'], request.args['devoir_id']])
    db.commit()
    return '', 200


@api.route('/role', methods=['GET'])
@jwt_required
def get_user_role():
    username = get_jwt_identity()
    print(username)
    return '', 200
    user_id = request.args['user_id']
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    r = c.execute("""
        SELECT 1 FROM enseignant
            WHERE mail = ? AND admin = 1;
    """, [user_id]).fetchone()
    if r:
        return '', 200
    return '', 404

@api.route('/protected', methods=['GET'])
@jwt_required
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200
