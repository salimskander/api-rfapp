from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
import os

load_dotenv()  # Charge les variables d'environnement depuis le fichier .env

app = Flask(__name__)

app.config['MONGO_URI'] = os.getenv('MONGO_URI')    # Utilisez os.getenv pour accéder à la variable d'environnement
mongo = PyMongo(app)

if "ssl_ca_certs" in app.config['MONGO_URI']:
    mongo.cx._topology.options.ssl_ca_certs = app.config['MONGO_URI']["ssl_ca_certs"]

@app.route('/')
def index():
    return jsonify({'message': 'Bienvenue a kiki ce gros 3goun'})

# Route pour créer un utilisateur
@app.route('/api/user', methods=['POST'])
def create_user():
    try:
        data = request.get_json()

        # Vérifiez si le nom d'utilisateur existe déjà
        if mongo.db.users.find_one({'username': data['username']}):
            return jsonify({'error': 'Ce nom d\'utilisateur existe déjà'}), 400

        # Hash du mot de passe avant de le stocker dans la base de données
        hashed_password = generate_password_hash(data['password'], method='pbkdf2')

        # Insérez l'utilisateur dans la base de données
        new_user = {
            'username': data['username'],
            'password': hashed_password
        }
        mongo.db.users.insert_one(new_user)

        return jsonify({'message': 'Utilisateur créé avec succès'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route pour récupérer tous les utilisateurs
@app.route('/api/user', methods=['GET'])
def get_users():
    try:
        users = mongo.db.users.find({}, {'_id': 0})
        user_list = [user for user in users]
        return jsonify({'users': user_list}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route pour récupérer un utilisateur par son nom d'utilisateur
@app.route('/api/user/<username>', methods=['GET'])
def get_user(username):
    try:
        user = mongo.db.users.find_one({'username': username}, {'_id': 0})
        if user:
            return jsonify(user), 200
        else:
            return jsonify({'message': 'Utilisateur non trouvé'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route pour mettre à jour un utilisateur par son nom d'utilisateur
@app.route('/api/user/<username>', methods=['PUT'])
def update_user(username):
    try:
        data = request.get_json()

        # Vérifiez si le nom d'utilisateur existe
        existing_user = mongo.db.users.find_one({'username': username})
        if not existing_user:
            return jsonify({'message': 'Utilisateur non trouvé'}), 404

        # Hash du nouveau mot de passe avant de le mettre à jour dans la base de données
        hashed_password = generate_password_hash(data['password'], method='sha256')

        # Mettez à jour l'utilisateur
        mongo.db.users.update_one({'username': username}, {'$set': {'password': hashed_password}})

        return jsonify({'message': 'Utilisateur mis à jour avec succès'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route pour supprimer un utilisateur par son nom d'utilisateur
@app.route('/api/user/<username>', methods=['DELETE'])
def delete_user(username):
    try:
        result = mongo.db.users.delete_one({'username': username})
        if result.deleted_count == 1:
            return jsonify({'message': 'Utilisateur supprimé avec succès'}), 200
        else:
            return jsonify({'message': 'Utilisateur non trouvé'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
