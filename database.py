from pymongo.errors import ConnectionFailure
from flask_pymongo import PyMongo
from pymongo import MongoClient
from pymongo.server_api import ServerApi

def connect_to_mongo(app):
    uri = app.config['MONGO_URI']
    client = MongoClient(uri, server_api=ServerApi('1'))

    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except ConnectionFailure as e:
        print(f"Error connecting to MongoDB: {e}")
        raise RuntimeError("Failed to connect to MongoDB")

    return PyMongo(app)
