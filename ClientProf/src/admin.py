import requests, flask_login
from flask import Blueprint, request, jsonify, render_template

admin = Blueprint('admin', __name__)

@admin.route('/')
@flask_login.login_required
def dashboard():
    print(dir(request))
    print(request.cookies)
    print(request.headers)
    role_r = requests.get('http://localhost:5000/api/role', params={'user_id': flask_login.current_user.id}, cookies=request.cookies)
    if role_r.status_code == 200:
        return render_template('admin.html', user = flask_login.current_user)
    return 'Error', 404
