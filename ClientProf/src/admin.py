import requests
from flask import Blueprint, request, jsonify, render_template

admin = Blueprint('admin', __name__)

@admin.route('/')
def dashboard():
    print(request.cookies)
    role_r = requests.get('http://localhost:5000/api/role', cookies=request.cookies)
    print(role_r.content)
    if role_r.status_code == 200:
        return render_template('admin.html', user = 'c')
    return 'Error', 404
