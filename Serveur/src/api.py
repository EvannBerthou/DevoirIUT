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

    pjs = []
    print(files)
    for filename, file in files.items():
        if filename != '':
            blob = file.stream.read()
            pjs.append((filename, blob))

    classes = args.getlist('classe')
    for classe in classes:
        c.execute("""
            INSERT INTO devoirs (enonce,matiere, prof, classe)
            VALUES (?, ?, ?, 
                (SELECT id FROM classes WHERE nom = ?));
        """,
        [enonce,matiere,prof,classe])

        last_id = (c.execute("SELECT id FROM devoirs WHERE id=(SELECT MAX(id) FROM devoirs);").fetchone()[0])

        for filename, blob in pjs:
            c.execute("INSERT INTO pj (devoir_id, nom, contenue) VALUES (?, ?, ?);", [last_id, filename, blob])

    db.commit()
    return jsonify({}), 200

def liste_devoirs(id_classe):
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    rows = c.execute("""
        SELECT devoirs.id, enonce, matiere, prof, jour, pj.id, nom,
        REPLACE(REPLACE(a_rendre, 0, 'Non'), 1, 'Oui') 
        FROM devoirs LEFT JOIN pj ON pj.devoir_id = devoirs.id
        WHERE devoirs.classe = (SELECT id FROM classes WHERE nom = ?);
    """,
    [id_classe])
    devoirs = c.fetchall()

    s = {}
    parsed = []
    for row in devoirs:
        devoir_id = row[0]
        if not devoir_id in s: # Si c'est la première fois qu'on rencontre un devoir avec cet id
            s[row[0]] = index = len(parsed) # Ajout l'id aux ids visités
            devoir = list(row[1:5]) + [[]] + list(row[7:])
            parsed.append(devoir)


        index = s[devoir_id]
        # S'il y a une pièce jointe
        if row[5] != None:
            # L'ajouter
            parsed[index][4].append([row[5], row[6]])

    return jsonify(parsed), 200

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
