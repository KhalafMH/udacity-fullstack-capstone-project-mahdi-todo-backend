from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate

from models import setup_db

app = Flask(__name__)
db = setup_db(app)
migrate = Migrate(app, db)

CORS(app)
