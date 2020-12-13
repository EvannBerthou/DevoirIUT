import sqlite3
import requests
from bs4 import BeautifulSoup

html = requests.get('http://chronos.iut-velizy.uvsq.fr/EDT/gindex.html').content
soup = BeautifulSoup(html, features='html.parser')
classes = soup.find('select').text.strip().split('\n')[2:]

db = sqlite3.connect('src/devoirs.db')
c = db.cursor()
sql_str = open('db.sql').read()
c.executescript(sql_str)

for classe in classes:
    c.execute('INSERT INTO classes (nom) VALUES (?);', [classe])

c.execute("INSERT INTO enseignant VALUES ('Marsan','Laurent','laurent.marsant@uvsq.fr','C'); ")
c.execute("INSERT INTO enseignant VALUES ('a','a','a','C'); ")

c.close()
db.commit()
