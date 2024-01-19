import os
from dotenv import load_dotenv
from flask import Flask


load_dotenv()

app = Flask(__name__)

class Config:
    MONGO_URI = os.getenv('MONGO_URI')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
   
    
    

