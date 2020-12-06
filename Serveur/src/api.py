import sqlite3, os, re
from flask import Blueprint, request, jsonify, send_from_directory

api = Blueprint('api', __name__)

def safe_name(name):
    keep = (' ','.','_')
    return "".join(c for c in name if c.isalnum() or c in keep).rstrip()

def ajouter_devoir(args, files):
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    enonce,matiere,prof = args["enonce"],args["matiere"],args["prof"]

    blob = ''
    filename = ''
    file_path = ''
    if files:
        filename = safe_name(next(iter(files.to_dict())))
        if filename != '':
            pj = files[filename]
            file_path = os.path.join('src', filename)
            pj.save(file_path)
            with open(file_path, 'rb') as f:
                blob = f.read()

    classes = args.getlist('classe')
    last_id = None
    if blob != '':
        c.execute("INSERT INTO pj (nom, contenue) VALUES (?, ?);", [filename, blob])
        last_id = (c.execute("SELECT id FROM pj WHERE id=(SELECT MAX(id) FROM pj);").fetchone()[0])

    for classe in classes:
        c.execute("""
            INSERT INTO devoirs (enonce,matiere, prof, pj, classe)
            VALUES (?, ?, ?, ?, 
                (SELECT id FROM classes WHERE nom = ?));
        """,
        [enonce,matiere,prof,last_id,classe])

    db.commit()
    if blob != '':
        os.remove(file_path)
    return jsonify({}), 200

def liste_devoirs(id_classe):
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    rows = c.execute("""
        SELECT enonce, matiere, prof, jour, 0, 0,
        REPLACE(REPLACE(a_rendre, 0, 'Non'), 1, 'Oui') 
        FROM devoirs
        WHERE devoirs.classe = (SELECT id FROM classes WHERE nom = ?)
            AND (devoirs.pj IS NULL)
        UNION
        SELECT enonce, matiere, prof, jour, pj.id, pj.nom,
        REPLACE(REPLACE(a_rendre, 0, 'Non'), 1, 'Oui') 
        FROM devoirs, pj
        WHERE devoirs.classe = (SELECT id FROM classes WHERE nom = ?)
            AND (devoirs.pj = pj.id)
    """,
    [id_classe, id_classe])
    devoirs = c.fetchall()
    print(devoirs)
    return jsonify(devoirs), 200

def is_connected(args):
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    pwd_entrer,email_entrer=args["pwd"],args['email']
    pwd=c.execute("""
        SELECT pwd 
        FROM enseignant
        WHERE mail=? ;
        """,
    [email_entrer])
    pwd=[pw for pw in pwd]
    if pwd:
        pwd=pwd[0][0]
        if pwd == pwd_entrer:
            data = c.execute(" SELECT nom,prenom FROM enseignant WHERE mail==?;",[email_entrer])
            return jsonify([dat for dat in data]),200
    return jsonify({}), 200



@api.route('/devoirs', methods=['GET', 'POST'])
def devoirs():
    if request.method == 'POST':
        return ajouter_devoir(request.args, request.files)
    elif request.method == 'GET':
        return liste_devoirs(request.args['classe'])


@api.route('/connexion')
def connect():
    return is_connected(request.args)

@api.route('/classe', methods=['GET'])
def classes():
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    rows = c.execute("""
        SELECT nom FROM classes;
    """)
    classes = [row for row in rows]
    return jsonify(classes), 200

@api.route('/pj', methods=['GET'])
def pj():
    pj_id = request.args['id']
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    rows = c.execute("""
        SELECT nom, contenue FROM pj WHERE id = ?;
    """,
    [pj_id])
    pj = c.fetchone()
    path = os.path.join('src', 'temp')
    open(path, 'wb').write(pj[1])
    c = open(path, 'rb').read()

    res = send_from_directory(directory='.', filename='temp', 
        as_attachment=True, attachment_filename=safe_name(pj[0]))
    os.remove(path)
    return res
