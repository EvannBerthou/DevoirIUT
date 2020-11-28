import sqlite3
from flask import Blueprint, request, jsonify

api = Blueprint('api', __name__)

def ajouter_devoir(args):
    print("Nouveau devoir")
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    enonce,prof = args["enonce"], args["prof"]
    print(enonce, prof)
    c.execute("INSERT INTO devoirs (enonce, prof) VALUES (?, ?);", [enonce, prof])
    db.commit()
    return jsonify({}), 200

def liste_devoirs():
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    rows = c.execute("SELECT * FROM devoirs")
    devoirs = [row for row in rows]
    return jsonify(devoirs), 200

@api.route('/devoirs', methods=['GET', 'POST'])
def devoirs():
    if request.method == 'POST':
        return ajouter_devoir(request.args)
    elif request.method == 'GET':
        return liste_devoirs()
