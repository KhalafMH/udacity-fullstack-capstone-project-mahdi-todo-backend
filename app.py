from re import match

from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from flask_migrate import Migrate

from auth import requires_auth_permission, AuthError, requires_auth_user
from models import setup_db, User, Todo

app = Flask(__name__)
db = setup_db(app)
migrate = Migrate(app, db)

CORS(app)


@app.route('/api/v1/users')
@requires_auth_permission('read:all-users')
def get_all_users(token_payload):
    """
    Returns the details of all the users in the database.

    :return: A 200 JSON response indicating the success of the request and a list with the details of all users
    """
    users = User.query.all()

    return jsonify({
        "success": True,
        "users": list(map(lambda x: x.json, users))
    })


@app.route('/api/v1/users/<string:user_id>')
@requires_auth_permission('read:own-user')
@requires_auth_user()
def get_user(token_payload, user_id):
    """
    Returns the details of user with ID `user_id`.

    :param user_id: The ID of the user.
    :return: A 200 JSON response indicating the success of the request and the details of the requested user.
    """
    user = User.query.get(user_id)
    if user is None:
        abort(404)

    return jsonify({
        "success": True,
        "user": user.json
    }), 200


@app.route('/api/v1/users/<string:user_id>', methods=['PUT'])
@requires_auth_permission('write:own-user')
@requires_auth_user()
def put_user(token_payload, user_id):
    """
    Adds a new user to the database.

    :return: A JSON object indicating the success of the request and the inserted user.
    """
    user_check = User.query.get(user_id)
    if user_check is not None:
        abort(409)

    name = request.json.get('name')
    email = request.json.get('email')
    user = User(id=user_id, name=name, email=email)
    result = user.persist()
    return jsonify({
        "success": True,
        "user": result.json
    }), 201


@app.route('/api/v1/users/<string:user_id>', methods=['PATCH'])
@requires_auth_permission('write:own-user')
@requires_auth_user()
def patch_user(token_payload, user_id):
    """
    Modifies a user in the database

    :param user_id: The id of the user record
    :return: A 200 JSON response indicating the success of the request and the new details of the user
    """
    if request.json is None:
        abort(415)  # unsupported media type

    name = request.json.get('name')
    email = request.json.get('email')

    if name is None and email is None:
        abort(400)

    if email is not None and not match('^[\w\d_]+@[\w\d_]+\.[\w\d_]+$', email):
        abort(400)

    user = User.query.get(user_id)
    if user is None:
        abort(404)

    user.name = name or user.name
    user.email = email or user.email

    persisted_user = user.persist()

    return jsonify({
        "success": True,
        "user": persisted_user.json
    }), 200


@app.route('/api/v1/users/<string:user_id>', methods=['DELETE'])
@requires_auth_permission('write:own-user')
@requires_auth_user()
def delete_user(token_payload, user_id):
    """
    Deletes a user from the database

    :param user_id: The id of the user
    :return: A 200 JSON response indicating the success of the request
    """
    user = User.query.get(user_id)
    if user is None:
        abort(404)

    success = user.delete()

    if success:
        return jsonify({
            "success": True
        }), 200
    else:
        abort(500)


@app.route('/api/v1/users/<string:user_id>/todos')
@requires_auth_permission('read:own-todos')
@requires_auth_user()
def get_todos(token_payload, user_id):
    """
    Returns the todos owned by a user.

    :param user_id: The ID of the user.
    :return: A 200 JSON response indicating the success of the request and the list of todos owned by the user.
    """
    user = User.query.get(user_id)
    if user is None:
        abort(404)

    return jsonify({
        "success": True,
        "user_id": user.id,
        "todos": [todo.json for todo in user.todos]
    }), 200


@app.route('/api/v1/users/<string:user_id>/todos', methods=['POST'])
@requires_auth_permission('write:own-todos')
@requires_auth_user()
def post_todo(token_payload, user_id):
    """
    Creates todos in the database for user with id `user_id`.

    :param user_id: The ID of the user for which todos will be created.
    :return: A 200 JSON response indicating the success of the request and the list of inserted todos.
    """
    if request.json is None:
        abort(415)

    todos = request.json
    if not isinstance(todos, list) or len(todos) == 0:
        abort(400)

    count_user = User.query.filter_by(id=user_id).count()
    if count_user == 0:
        abort(404)

    response_todos = []
    for todo in todos:
        done = todo.get('done') or False
        title = todo.get('title')
        if title is None:
            abort(400)
        new_todo = Todo(owner_id=user_id, title=title, done=done)
        clone = new_todo.persist()
        response_todos.append(clone.json)

    return jsonify({
        "success": True,
        "user_id": user_id,
        "todos": response_todos
    }), 200


@app.route('/api/v1/users/<string:user_id>/todos/<int:todo_id>', methods=['PATCH'])
@requires_auth_permission('write:own-todos')
@requires_auth_user()
def patch_todo(token_payload, user_id, todo_id):
    """
    Modifies a todo for user with `user_id` in the database.

    :param user_id: The ID of the owner of the todo
    :param todo_id: The ID of the todo
    :return: A 200 JSON response indicating the success of the request and the modified todo
    """
    todo = Todo.query.get(todo_id)
    if todo is None:
        abort(404)

    if request.json is None:
        abort(415)

    if not isinstance(request.json, dict):
        abort(400)

    new_title = request.json.get('title')
    new_done = request.json.get('done')
    if new_title is None and new_done is None:
        abort(400)

    todo.title = new_title or todo.title
    todo.done = new_done or todo.done
    todo.persist()
    return jsonify({
        "success": True,
        "user_id": todo.owner_id,
        "todo": todo.json
    }), 200


@app.route('/api/v1/users/<string:user_id>/todos/<int:todo_id>', methods=['DELETE'])
@requires_auth_permission('write:own-todos')
@requires_auth_user()
def delete_todo(token_payload, user_id, todo_id):
    """
    Deletes a user todo from the database.

    :param user_id: The ID of the user who owns the todo.
    :param todo_id: The ID of the todo.
    :return: A 200 JSON response indicating the success of the request.
    """
    todo = Todo.query.get(todo_id) or abort(404)
    success = todo.delete()
    if success:
        return jsonify({
            "success": True
        }), 200
    else:
        abort(500)


@app.errorhandler(400)
def handle_400(error):
    return jsonify({
        "success": False,
        "message": "Invalid request"
    }), 400


@app.errorhandler(AuthError)
def handle_401(error):
    return jsonify({
        "success": False,
        "message": "Not authorized"
    }), 401


@app.errorhandler(404)
def handle_404(error):
    return jsonify({
        "success": False,
        "message": "Resource not found"
    }), 404


@app.errorhandler(409)
def handle_409(error):
    return jsonify({
        "success": False,
        "message": "Conflict"
    }), 409


@app.errorhandler(415)
def handle_415(error):
    return jsonify({
        "success": False,
        "message": "Invalid content type"
    }), 415


@app.errorhandler(500)
def handle_500(error):
    return jsonify({
        "success": False,
        "message": "Internal error"
    }), 500
