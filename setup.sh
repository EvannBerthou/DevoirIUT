echo "Création du venv Client"
python3 -m venv Client/venv
echo "Création du venv Serveur"
python3 -m venv Serveur/venv

echo "Setup client"
cd Client
source ./venv/bin/activate
echo "Installation packages"
pip install -r requirements.txt
echo "source ./venv/bin/activate; export FLASK_APP=src/main.py" > activate.sh
chmod +x activate.sh
deactivate

cd ..

echo "Setup serveur"
cd Serveur
source ./venv/bin/activate
echo "source ./venv/bin/activate; export FLASK_APP=src/main.py" > activate.sh
chmod +x activate.sh
echo "Installation packages"
pip install -r requirements.txt
echo "Setup db"
python setup_db.py
deactivate

echo "Installation complète !"
