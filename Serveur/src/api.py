import sqlite3
from flask import Blueprint, request, jsonify, send_from_directory, send_file
from werkzeug.security import generate_password_hash, check_password_hash

from flask_jwt_extended import (
    jwt_required, create_access_token, jwt_optional,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity, set_access_cookies,
    set_refresh_cookies, unset_jwt_cookies
)

api = Blueprint('api', __name__)

def safe_name(name):
    keep = (' ','.','_')
    return "".join(c for c in name if c.isalnum() or c in keep).rstrip()

def devoir_classe(classe):
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
        WHERE
           did IN (SELECT devoir_id FROM devoir_classe, classes
                          WHERE classe_id = classes.id AND classes.nom = ?);
    """,
    [classe]).fetchall()

def devoir_enseignant(username):
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
       WHERE
           matiere IN (SELECT nom
                       FROM matiere
                       WHERE id
                       IN (SELECT matiere_id
                           FROM matiere_enseignant, enseignant
                           WHERE enseignant_id = enseignant.id AND mail = ?)
           );
    """,
    [username]).fetchall()


def get_class(id_devoir):
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    return c.execute("""
        SELECT nom
        FROM classes
        WHERE id IN (SELECT classe_id
                    FROM devoir_classe
                    WHERE devoir_id=? );
        """,[id_devoir]).fetchall()


# Fusionne les colonnes afin d'avoir les pièces jointes dans une liste
def merge_pj(devoirs):
    parsed = {}
    for row in devoirs:
        devoir_id = row[0]
        if not devoir_id in parsed: # Si c'est la première fois qu'on rencontre un devoir avec cet id
            parsed[devoir_id] = list(row[0:5]) + [[]] + list(row[7:]) + [[classe[0] for classe in get_class(devoir_id)]]
        # S'il y a une pièce jointe
        if row[5]:
            parsed[devoir_id][5].append((str(row[5]), row[6]))
    return list(parsed.values())



@api.route('/devoirs', methods=['POST'])
@jwt_required
def ajouter_devoir():
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
    return '', 200

@api.route('/devoirs', methods=['GET'])
@jwt_optional
def liste_devoirs():
    if 'classe' in request.args:
        devoirs = merge_pj(devoir_classe(request.args['classe']))
        return jsonify(devoirs=devoirs), 200
    else:
        username = get_jwt_identity()
        devoirs = merge_pj(devoir_enseignant(username))
        return jsonify(user=username, devoirs=devoirs), 200


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

@api.route('/classe', methods=['GET'])
def classes():
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    classes = c.execute("SELECT nom FROM classes;").fetchall()
    return jsonify(classes), 200

@api.route('/enseignant', methods=['GET'])
def enseignants():
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    enseignants = c.execute("SELECT id,nom,prenom,mail FROM enseignant;").fetchall()
    return jsonify(enseignants), 200

@api.route('/matieres', methods=['GET'])
@jwt_required
def matieres():
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()

    matieres = c.execute("""
        SELECT nom FROM matiere
        WHERE id IN
            (SELECT matiere_id FROM matiere_enseignant
                WHERE enseignant_id = (SELECT id FROM enseignant WHERE mail = ?));
    """,
    [get_jwt_identity()]).fetchall()
    return jsonify(matieres), 200

@api.route('/pj', methods=['GET'])
def pj():
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
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    r = c.execute("""
        SELECT 1 FROM enseignant
            WHERE mail = ? AND admin = 1;
    """, [username]).fetchone()
    if r:
        return jsonify(user=get_jwt_identity()), 200
    return '', 404

@api.route('/classe_enseignant', methods=['GET'])
@jwt_required
def classe_enseignants():
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    ce = c.execute("""
        SELECT classes.nom, mail
        FROM classes, enseignant, classe_enseignant
        WHERE enseignant.id = classe_enseignant.enseignant_id
            AND classes.id = classe_enseignant.classe_id;
    """).fetchall()
    return jsonify(ce), 200

@api.route('/gestion_classe', methods=['DELETE'])
@jwt_required
def remove_classe():
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    r = c.execute("DELETE FROM classes WHERE nom = ?;", [request.args['classe']])
    db.commit()
    return '', 200

# TODO: Faire en sorte que l'id soit l'id et non le nom
@api.route('/gestion_classe', methods=['PATCH'])
@jwt_required
def modif_classe():
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    c.execute("UPDATE classes SET nom = ? WHERE nom = ?;", [request.args['nom'], request.args['id']])
    c.execute("DELETE FROM classe_enseignant WHERE classe_id = (SELECT id FROM classes WHERE nom = ?);", [request.args['id']])
    for e in request.args.getlist('enseignants'):
        c.execute("""
                INSERT INTO classe_enseignant VALUES
                    (
                        (SELECT id FROM enseignant WHERE mail = ?),
                        (SELECT id FROM classes WHERE nom = ?)
                    );
        """, [e, request.args['id']])
    db.commit()
    return '', 200

@api.route('/gestion_classe', methods=['POST'])
@jwt_required
def ajouter_classe():
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    r = c.execute("INSERT INTO classes(nom) VALUES (?);", [request.args['name'].replace(' ', '-')])
    db.commit()
    return '', 200

@api.route('/gestion_enseignant', methods=['DELETE'])
@jwt_required
def remove_enseignant():
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    r = c.execute("DELETE FROM enseignant WHERE mail = ?;", [request.args['enseignant']])
    db.commit()
    return '', 200

@api.route('/gestion_enseignant', methods=['PATCH'])
@jwt_required
def modif_enseignant():
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    mdp = generate_password_hash(request.args['mdp']) if request.args['mdp'] else None
    r = c.execute("""UPDATE enseignant SET
        nom = ?, prenom = ?, mail = ?, pwd = IFNULL(?, pwd)
        WHERE id = ?;
    """, [request.args['nom'], request.args['prenom'], request.args['mail'], mdp, request.args['id']])
    db.commit()
    return '', 200

@api.route('/gestion_enseignant', methods=['POST'])
@jwt_required
def ajouter_enseignant():
    print('t')
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    pwd = generate_password_hash(request.args['mdp'])
    r = c.execute("INSERT INTO enseignant(nom,prenom,mail,pwd,admin) VALUES (?,?,?,?,0);", [
        request.args['nom'],
        request.args['prenom'],
        request.args['mail'],
        pwd])
    db.commit()
    return '', 200

"""
AUTH JWT
"""

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
    pass_found = c.execute('SELECT pwd FROM enseignant WHERE mail = ?;', [username]).fetchone()
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
def refresh():
    # Create the new access token
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    # Set the JWT access cookie in the response
    resp = jsonify({'refresh': True})
    set_access_cookies(resp, access_token)
    return resp, 200

@api.route('/token/remove', methods=['POST'])
def logout():
    resp = jsonify({'logout': True})
    unset_jwt_cookies(resp)
    return resp, 200

