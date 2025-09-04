from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager

mongo_client = PyMongo()
jwt_client = JWTManager()