from flask import Flask
from dotenv import load_dotenv
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager
import os

load_dotenv()

app = Flask(__name__)
app.config['MONGO_URI'] = os.getenv('MONGO_URI')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
mongo = PyMongo(app)
jwt = JWTManager(app)

if "ssl_ca_certs" in app.config['MONGO_URI']:
    mongo.cx._topology.options.ssl_ca_certs = app.config['MONGO_URI']["ssl_ca_certs"]

if __name__ == '__main__':
    app.run(debug=True)
