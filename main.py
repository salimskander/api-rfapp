from dotenv import load_dotenv
from flask import Flask
import os
from database import connect_to_mongo
from routes.user_routes import user_routes
from routes.auth_routes import auth_routes
from flask_jwt_extended import JWTManager

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['MONGO_URI'] = os.getenv('MONGO_URI')
jwt = JWTManager(app)
mongo = connect_to_mongo(app)
app.register_blueprint(user_routes)
app.register_blueprint(auth_routes)

if __name__ == '__main__':
    app.run(debug=False)
