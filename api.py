from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import os

load_dotenv()  # Charge les variables d'environnement depuis le fichier .env

app = Flask(__name__)
app.config['MONGO_URI'] = os.getenv('MONGO_URI')    # Utilisez os.getenv pour accéder à la variable d'environnement
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')  # Clé secrète pour JWT
mongo = PyMongo(app)
jwt = JWTManager(app)

if "ssl_ca_certs" in app.config['MONGO_URI']:
    mongo.cx._topology.options.ssl_ca_certs = app.config['MONGO_URI']["ssl_ca_certs"]

# Gestion des erreurs 500 (Internal Server Error)
@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({'error': 'Erreur interne du serveur'}), 500

@app.route('/')
def index():
    return jsonify({'message': 'Bienvenue a kiki ce gros 3goun'})

# Route pour créer un utilisateur
@app.route('/api/user', methods=['POST'])
def create_user():
    try:
        data = request.get_json()

        # Vérifiez si le nom d'utilisateur ou le mot de passe est vide
        if not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Le nom d\'utilisateur et le mot de passe sont requis'}), 400

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

# Route pour authentifier un utilisateur et générer un token JWT
@app.route('/api/auth', methods=['POST'])
def authenticate_user():
    try:
        data = request.get_json()

        # Vérifiez si le nom d'utilisateur et le mot de passe sont fournis
        if not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Le nom d\'utilisateur et le mot de passe sont requis'}), 400

        # Récupérez l'utilisateur depuis la base de données
        user = mongo.db.users.find_one({'username': data['username']}, {'_id': 0})

        # Vérifiez si l'utilisateur existe et si le mot de passe est correct
        if user and check_password_hash(user['password'], data['password']):
            # Générez un token JWT
            access_token = create_access_token(identity=data['username'])
            return jsonify(access_token=access_token), 200
        else:
            return jsonify({'error': 'Nom d\'utilisateur ou mot de passe incorrect'}), 401

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Exemple d'une route protégée par JWT
@app.route('/api/protected', methods=['GET'])
@jwt_required()
def protected():
    # Accédez à l'identité du courant utilisateur via get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

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
