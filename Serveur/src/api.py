import sqlite3
from flask import Blueprint, request, jsonify

api = Blueprint('api', __name__)

def ajouter_devoir(args):
    print("Nouveau devoir")
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    enonce,prof = args["enonce"], args["prof"]
    classes = args.getlist('classe')
    for classe in classes:
        c.execute("""
            INSERT INTO devoirs (enonce, prof, classe)
            VALUES (?, ?, 
                (SELECT id FROM classes WHERE nom = ?));
        """,
        [enonce, prof, classe])

    db.commit()
    return jsonify({}), 200

def liste_devoirs(id_classe):
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    rows = c.execute("""
        SELECT enonce, prof, jour, 
            REPLACE(REPLACE(a_rendre, 0, 'Non'), 1, 'Oui')
        FROM devoirs, classes
        WHERE devoirs.classe = classes.id
        AND classes.nom = ?;
    """,
    [id_classe])
    devoirs = [row for row in rows]
    return jsonify(devoirs), 200

@api.route('/devoirs', methods=['GET', 'POST'])
def devoirs():
    if request.method == 'POST':
        return ajouter_devoir(request.args)
    elif request.method == 'GET':
        return liste_devoirs(request.args['classe'])

@api.route('/classe', methods=['GET'])
def classes():
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    rows = c.execute("""
        SELECT nom FROM classes;
    """)
    classes = [row for row in rows]
    return jsonify(classes), 200
