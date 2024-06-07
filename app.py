import hashlib

import pymongo
from flask import Flask, jsonify, request
from flask_pymongo import PyMongo

from config import MONGO_URI

app = Flask(__name__)
app.config["MONGO_URI"] = MONGO_URI
mongo = PyMongo(app)


@app.route("/addPatient", methods=["POST"])
def add_patient():
    data = request.get_json()

    if not data or not all(
        key in data
        for key in ("nom", "prenom", "date_naissance", "genre", "groupe_sanguin")
    ):
        return jsonify({"error": "Données incomplètes"}), 400

    nom = data["nom"]
    prenom = data["prenom"]
    date_naissance = data["date_naissance"]
    genre = data["genre"]
    groupe_sanguin = data["groupe_sanguin"]

    patient_id = hashlib.sha256(f"{nom}{prenom}".encode()).hexdigest()

    patient = {
        "_id": patient_id,
        "nom": nom,
        "prenom": prenom,
        "date_naissance": date_naissance,
        "genre": genre,
        "groupe_sanguin": groupe_sanguin,
    }

    try:
        mongo.db.patients.insert_one(patient)
    except pymongo.errors.DuplicateKeyError:
        return jsonify({"error": "Patient avec cet ID existe déjà"}), 400

    return jsonify({"message": "Patient ajouté avec succès"}), 201


if __name__ == "__main__":
    app.run(debug=True)
