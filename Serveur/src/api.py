import sqlite3
from flask import Blueprint, request, jsonify

api = Blueprint('api', __name__)

def ajouter_devoir(args):
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    enonce,matiere,prof = args["enonce"],args["matiere"],args["prof"]
    classes = args.getlist('classe')
    for classe in classes:
        c.execute("""
            INSERT INTO devoirs (enonce,matiere, prof, classe)
            VALUES (?, ?, ?, 
                (SELECT id FROM classes WHERE nom = ?));
        """,
        [enonce,matiere,prof,classe])

    db.commit()
    return jsonify({}), 200

def liste_devoirs(id_classe):
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    rows = c.execute("""
        SELECT enonce, matiere, prof, jour,
        REPLACE(REPLACE(a_rendre, 0, 'Non'), 1, 'Oui')
        FROM devoirs, classes
        WHERE devoirs.classe = classes.id
        AND classes.nom = ?;
    """,
    [id_classe])
    devoirs=[row for row in rows]
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
            data=c.execute(" SELECT nom,prenom FROM enseignant WHERE mail==?;",[email_entrer])
            return jsonify([dat for dat in data]),200
    return jsonify({}), 200



@api.route('/devoirs', methods=['GET', 'POST'])
def devoirs():
    if request.method == 'POST':
        return ajouter_devoir(request.args)
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
