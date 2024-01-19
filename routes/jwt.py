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