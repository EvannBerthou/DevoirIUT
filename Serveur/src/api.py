from flask import Blueprint, request, jsonify

api = Blueprint('api', __name__)

aliste_devoirs = []

def ajouter_devoir(args):
    print("Nouveau devoir")
    aliste_devoirs.append(args['devoir'])
    return 'ajouté'

def liste_devoirs():
    return jsonify(aliste_devoirs)

@api.route('/devoirs', methods=['GET', 'POST'])
def devoirs():
    if request.method == 'POST':
        return ajouter_devoir(request.args)
    elif request.method == 'GET':
        return liste_devoirs()
