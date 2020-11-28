import sqlite3

db = sqlite3.connect('src/devoirs.db')
c = db.cursor()

c.execute("""
    CREATE TABLE devoirs (
        enonce TEXT,
        prof INT,
        jour date DEFAULT (date(datetime('now', '+1 day', 'localtime'))),
        a_rendre INT DEFAULT 0
    );
""")

c.execute("""
    INSERT INTO devoirs (enonce, prof) VALUES ('Devoir 1', 0), ('Devoir 2', 1);
""")

c.close()
db.commit()
