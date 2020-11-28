import requests

d = input('Devoir : ')
requests.post('http://localhost:5000/api/devoirs', params={'enonce': d, "prof": 2})
