from re import match

from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from flask_migrate import Migrate

from models import setup_db, User

app = Flask(__name__)
db = setup_db(app)
migrate = Migrate(app, db)

CORS(app)


@app.route('/api/v1/users/<id>')
def get_user(id):
    user = User.query.get(id)
    if user is None:
        abort(404)

    return jsonify({
        "success": True,
        "user": user.json
    })


@app.route('/api/v1/users', methods=['POST'])
def post_user():
    """
    Adds a new user to the database.

    :return: A JSON object indicating the success of the request and the inserted user.
    """
    name = request.json.get('name')
    email = request.json.get('email')
    user = User(name=name, email=email)
    result = user.persist()
    return jsonify({
        "success": True,
        "user": result.json
    }), 201


@app.route('/api/v1/users/<id>', methods=['PATCH'])
def patch_user(id):
    """
    Modifies a user in the database

    :param id: The id of the user record
    :return: A JSON response indicating the success of the request and the new details of the user
    """
    if request.json is None:
        abort(415)  # unsupported media type

    name = request.json.get('name')
    email = request.json.get('email')

    if name is None and email is None:
        abort(400)

    if email is not None and not match('^[\w\d_]+@[\w\d_]+\.[\w\d_]+$', email):
        abort(400)

    user = User.query.get(id)
    if user is None:
        abort(404)

    user.name = name or user.name
    user.email = email or user.email

    persisted_user = user.persist()

    return jsonify({
        "success": True,
        "user": persisted_user.json
    }), 200


@app.route('/api/v1/users/<id>', methods=['DELETE'])
def delete_user(id):
    """
    Deletes a user from the database

    :param id: The id of the user
    :return: A JSON response indicating the success of the request
    """
    user = User.query.get(id)
    if user is None:
        abort(404)

    user.delete()

    return jsonify({
        "success": True
    }), 200
