import requests, json
from flask import Blueprint, request, jsonify, render_template

admin = Blueprint('admin', __name__)

@admin.route('/')
def dashboard():
    print(request.cookies)
    role_r = requests.get('http://localhost:5000/api/role', cookies=request.cookies)
    if role_r.status_code == 200:
        print('content', role_r.content)
        resp = json.loads(role_r.content)
        return render_template('admin.html', user = resp['user'])
    return 'Error', 404
