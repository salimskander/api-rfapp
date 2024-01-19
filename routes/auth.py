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

