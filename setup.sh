#!/bin/bash
setup () {
    echo "Création de $1/venv"
    python3 -m venv $1/venv

    cd $1
    echo "$(pwd)"
    source ./venv/bin/activate
    echo "Installation packages"
    pip install -r requirements.txt
    echo "source ./venv/bin/activate; export FLASK_APP=src/main.py;" > activate.sh
    chmod +x activate.sh
    echo "flask run --port=$2" > run.sh
    chmod +x run.sh
    deactivate
    cd ..
}

setup "Serveur" 5000
setup "ClientEleve" 5001
setup "ClientProf" 5002

echo "Installation terminée"
