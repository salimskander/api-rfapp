from flask import Blueprint, request, jsonify
from models.User import User
from flask_pymongo import PyMongo
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, create_refresh_token

auth_routes = Blueprint('auth_routes', __name__, url_prefix='/api/auth')

@auth_routes.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'error': 'Le nom d\'utilisateur et le mot de passe sont requis'}), 400

        if PyMongo(current_app).db.users.find_one({'username': data['username']}):
            return jsonify({'error': 'Ce nom d\'utilisateur existe déjà'}), 400

        hashed_password = generate_password_hash(data['password'], method='pbkdf2')

        new_user = User(username, hashed_password)

        user_data = {
            'username': new_user.username,
            'password_hash': new_user.password,
        }
        
        PyMongo(current_app).db.users.insert_one(user_data)

        return jsonify({'message': 'Utilisateur créé avec succès'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@auth_routes.route('/login', methods=['POST'])
def authenticate_user():
    try:
        data = request.get_json()

        if not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Le nom d\'utilisateur et le mot de passe sont requis'}), 400

        user = PyMongo(current_app).db.users.find_one({'username': data['username']}, {'_id': 0})

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

@auth_routes.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    try:
        current_user = get_jwt_identity()
        new_access_token = create_access_token(identity=current_user)
        return jsonify(access_token=new_access_token), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_routes.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200