import sqlite3
import requests
from bs4 import BeautifulSoup

html = requests.get('http://chronos.iut-velizy.uvsq.fr/EDT/gindex.html').content
soup = BeautifulSoup(html, features='html.parser')
classes = soup.find('select').text.strip().split('\n')[2:]

db = sqlite3.connect('src/devoirs.db')
c = db.cursor()

c.execute('DROP TABLE IF EXISTS classes')
c.execute('CREATE TABLE classes (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT);')

for classe in classes:
    c.execute('INSERT INTO classes (nom) VALUES (?);', [classe])

c.execute('DROP TABLE IF EXISTS devoirs')
c.execute("""
    CREATE TABLE devoirs (
        enonce TEXT,
        classe INT,
        matiere TEXT,
        prof INT,
        jour date DEFAULT (date(datetime('now', '+1 day', 'localtime'))),
        a_rendre INT DEFAULT 0,
        FOREIGN KEY(classe) REFERENCES classes(id)
    );
""")

c.execute('DROP TABLE IF EXISTS enseignant')
c.execute("""
    CREATE TABLE enseignant (
    	nom TEXT,
    	prenom TEXT,
    	mail TEXT,
    	pwd TEXT);
""")

c.execute("INSERT INTO enseignant VALUES ('Marsan','Laurent','laurent.marsant@uvsq.fr','C'); ")

c.close()
db.commit()
