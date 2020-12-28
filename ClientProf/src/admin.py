import requests, json
from flask import Blueprint, request, jsonify, render_template, redirect

admin = Blueprint('admin', __name__)

def valid_access():
    role_r = requests.get('http://localhost:5000/api/role', cookies=request.cookies)
    if role_r.status_code == 200:
        return json.loads(role_r.content)
    return None

def liste_classes():
    classes_r = requests.get('http://localhost:5000/api/classe')
    if classes_r.status_code == 200:
        return [''.join(classe) for classe in json.loads(classes_r.content)]
    return None

@admin.route('/')
def dashboard():
    if (resp := valid_access()):
        return render_template('admin.html', user = resp['user'])
    return 'Error', 404

@admin.route('/classes', methods=['GET'])
def gestion_classes():
    if (resp := valid_access()):
        classes = liste_classes()
        return render_template('classes.html', user = resp['user'], classes=classes)
    return 'Error', 404

@admin.route('/classes', methods=['POST'])
def suppr_classes():
    if (resp := valid_access()):
        if 'original' in request.form:
            requests.patch('http://localhost:5000/api/gestion_classe', cookies=request.cookies,
                    params={'old': request.form['original'], 'new': request.form['new']})
        else:
            requests.delete('http://localhost:5000/api/gestion_classe', cookies=request.cookies, params={'classe': request.form['suppr']})
        return redirect('/admin/classes')
    return 'Error', 404
