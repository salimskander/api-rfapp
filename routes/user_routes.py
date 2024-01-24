from flask import Blueprint, request, jsonify
from models.User import User
from flask_pymongo import PyMongo
from flask import current_app
from flask_jwt_extended import jwt_required

user_routes = Blueprint('user_routes', __name__, url_prefix='/api/users')

@user_routes.route('/', methods=['GET'])
def get_users():
    try:
        users = PyMongo(current_app).db.users.find({}, {'_id': 0})
        user_list = [user for user in users]
        return jsonify({'users': user_list}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@user_routes.route('/<username>', methods=['GET'])
@jwt_required()
def get_user(username):
    try:
        user = PyMongo(current_app).db.users.find_one({'username': username }, {'_id': 0 })
        if user:
            return jsonify({'username': user.get('username')}), 200
        else:
            return jsonify({'message': 'Utilisateur non trouvé'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@user_routes.route('/<username>', methods=['PATCH'])
@jwt_required()
def update_user(username):
    try:
        data = request.get_json()

        existing_user = PyMongo(current_app).db.users.find_one({'username': username})
        if not existing_user:
            return jsonify({'message': 'Utilisateur non trouvé'}), 404

        PyMongo(current_app).db.users.update_one({'username': username}, {"$set" : {"username" : data.get('username')}})

        return jsonify({'message': 'Utilisateur mis à jour avec succès'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_routes.route('/<username>', methods=['DELETE'])
@jwt_required()
def delete_user(username):
    try:
        result = PyMongo(current_app).db.users.delete_one({'username': username})
        if result.deleted_count == 1:
            return jsonify({'message': 'Utilisateur supprimé avec succès'}), 200
        else:
            return jsonify({'message': 'Utilisateur non trouvé'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500