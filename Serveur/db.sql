DROP TABLE IF EXISTS classes;
CREATE TABLE classes (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT NOT NULL);

DROP TABLE IF EXISTS devoirs;
CREATE TABLE devoirs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enonce TEXT,
    classe INT,
    matiere TEXT,
    prof INT,
    jour date DEFAULT (date(datetime('now', '+1 day', 'localtime'))),
    a_rendre INT DEFAULT 0,
    FOREIGN KEY(classe) REFERENCES classes(id)
);


DROP TABLE IF EXISTS pj;
CREATE TABLE pj (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    devoir_id INT,
    nom TEXT NOT NULL,
    contenue BLOB NOT NULL,
    FOREIGN KEY (devoir_id) REFERENCES devoirs(id)
);

DROP TABLE IF EXISTS enseignant;
CREATE TABLE enseignant (
    nom TEXT,
    prenom TEXT,
    mail TEXT,
    pwd TEXT
);
