from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import setup_db, User

app = Flask(__name__)
db = setup_db(app)
migrate = Migrate(app, db)

CORS(app)


@app.route('/api/v1/users', methods=['POST'])
def post_user():
    '''
    Adds a new user to the database.

    :return: A JSON object indicating the success of the request and the inserted user.
    '''
    name = request.json.get('name')
    email = request.json.get('email')
    user = User(name=name, email=email)
    result = user.persist()
    return jsonify({
        "success": True,
        "user": result.json
    }), 201
