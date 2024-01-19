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