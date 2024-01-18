from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, create_refresh_token
import os

load_dotenv()

app = Flask(__name__)
app.config['MONGO_URI'] = os.getenv('MONGO_URI')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
mongo = PyMongo(app)
jwt = JWTManager(app)

if "ssl_ca_certs" in app.config['MONGO_URI']:
    mongo.cx._topology.options.ssl_ca_certs = app.config['MONGO_URI']["ssl_ca_certs"]

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({'error': 'Erreur interne du serveur'}), 500

@app.route('/')
def index():
    return jsonify({'message': 'Bienvenue a kiki ce gros 3goun'})

@app.route('/api/user', methods=['POST'])
def create_user():
    try:
        data = request.get_json()

        if not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Le nom d\'utilisateur et le mot de passe sont requis'}), 400

        if mongo.db.users.find_one({'username': data['username']}):
            return jsonify({'error': 'Ce nom d\'utilisateur existe déjà'}), 400

        hashed_password = generate_password_hash(data['password'], method='pbkdf2')

        new_user = {
            'username': data['username'],
            'password': hashed_password
        }
        mongo.db.users.insert_one(new_user)

        return jsonify({'message': 'Utilisateur créé avec succès'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth', methods=['POST'])
def authenticate_user():
    try:
        data = request.get_json()

        if not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Le nom d\'utilisateur et le mot de passe sont requis'}), 400

        user = mongo.db.users.find_one({'username': data['username']}, {'_id': 0})

        if user and check_password_hash(user['password'], data['password']):
            # Message d'authentification réussie
            success_message = 'Authentification réussie'

            access_token = create_access_token(identity=data['username'])
            refresh_token = create_refresh_token(identity=data['username'])
            return jsonify(message=success_message, access_token=access_token, refresh_token=refresh_token), 200
        else:
            return jsonify({'error': 'Nom d\'utilisateur ou mot de passe incorrect'}), 401

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/token/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    try:
        current_user = get_jwt_identity()
        new_access_token = create_access_token(identity=current_user)
        return jsonify(access_token=new_access_token), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

@app.route('/api/user', methods=['GET'])
def get_users():
    try:
        users = mongo.db.users.find({}, {'_id': 0})
        user_list = [user for user in users]
        return jsonify({'users': user_list}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

@app.route('/api/user/<username>', methods=['PUT'])
def update_user(username):
    try:
        data = request.get_json()

        existing_user = mongo.db.users.find_one({'username': username})
        if not existing_user:
            return jsonify({'message': 'Utilisateur non trouvé'}), 404

        hashed_password = generate_password_hash(data['password'], method='sha256')
        mongo.db.users.update_one({'username': username}, {'$set': {'password': hashed_password}})

        return jsonify({'message': 'Utilisateur mis à jour avec succès'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
