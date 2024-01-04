from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from flask_restful import Api
from flask_jwt_extended import JWTManager

app = Flask(__name__)

app.config.from_pyfile('config.py', silent=True)
app.config['JWT_SECRET_KEY'] = "Sharii Anatolii"
app.config['JWT_ALGORITHM'] = "HS256"
db = SQLAlchemy(app)
migrate = Migrate(app, db)
api = Api(app)


import myapp.views

import myapp.models
