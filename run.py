from dotenv import load_dotenv
from flask import Flask
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
from config import app
import sys, os

load_dotenv()
uri = os.getenv('MONGO_URI')

client = MongoClient(uri, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
    sys.exit()

if __name__ == '__main__':
    app.run(debug=True)