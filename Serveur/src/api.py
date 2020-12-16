import sqlite3, os, io
from flask import Blueprint, request, jsonify, send_from_directory, send_file
from werkzeug.security import generate_password_hash, check_password_hash

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

def liste_devoirs(id_classe):
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
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
    [id_classe]).fetchall()

    # Fusionne les colonnes afin d'avoir les pièces jointes dans une liste
    parsed = {}
    for row in devoirs:
        devoir_id = row[0]
        if not devoir_id in parsed: # Si c'est la première fois qu'on rencontre un devoir avec cet id
            parsed[devoir_id] = list(row[1:5]) + [[]] + list(row[7:])

        # S'il y a une pièce jointe
        if row[5]:
            parsed[devoir_id][4].append((row[5], row[6]))

    return jsonify(list(parsed.values())), 200

@api.route('/login', methods=['GET'])
def login():
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()

    pwd, email_entrer = request.args['pwd'], request.args['email']
    pass_found = c.execute('SELECT pwd FROM enseignant WHERE mail = ?;', [email_entrer]).fetchone()
    if pass_found and check_password_hash(pass_found[0], pwd):
        return '', 200
    return '', 404

@api.route('/user', methods=['GET'])
def user():
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    email = request.args['email']
    user_found = c.execute('SELECT 1 FROM enseignant WHERE mail = ?', [email]).fetchone()
    return '', 404 if user_found == None else 200

@api.route('/devoirs', methods=['GET', 'POST'])
def devoirs():
    if request.method == 'POST':
        return ajouter_devoir(request.args, request.files)
    elif request.method == 'GET':
        return liste_devoirs(request.args['classe'])

@api.route('/classe', methods=['GET'])
def classes():
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    classes = c.execute("SELECT nom FROM classes;").fetchall()
    return jsonify(classes), 200

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
