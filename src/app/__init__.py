from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_request_validator.exceptions import InvalidRequest
from flask_jwt_simple import JWTManager
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

@app.errorhandler(InvalidRequest)
def invalid_data(e):
    return {"error": e.message}, 422

@app.errorhandler(HTTPException)
def http_error_handler(e):
    return {"error": e.description}, e.code

from app import endpoints