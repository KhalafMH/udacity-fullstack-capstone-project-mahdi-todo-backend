from re import match

from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from flask_migrate import Migrate

from models import setup_db, User, Todo

app = Flask(__name__)
db = setup_db(app)
migrate = Migrate(app, db)

CORS(app)


@app.route('/api/v1/users/<int:user_id>')
def get_user(user_id):
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


@app.route('/api/v1/users/<int:id>', methods=['PATCH'])
def patch_user(id):
    """
    Modifies a user in the database

    :param id: The id of the user record
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


@app.route('/api/v1/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    """
    Deletes a user from the database

    :param id: The id of the user
    :return: A 200 JSON response indicating the success of the request
    """
    user = User.query.get(id)
    if user is None:
        abort(404)

    user.delete()

    return jsonify({
        "success": True
    }), 200


@app.route('/api/v1/users/<int:user_id>/todos')
def get_todos(user_id):
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


@app.route('/api/v1/users/<int:user_id>/todos', methods=['POST'])
def post_todo(user_id):
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


@app.route('/api/v1/users/<int:user_id>/todos/<int:todo_id>', methods=['PATCH'])
def patch_todo(user_id, todo_id):
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
    print(f'title: {todo.title}, done: {todo.done}')
    todo.persist()
    return jsonify({
        "success": True,
        "user_id": todo.owner_id,
        "todo": todo.json
    }), 200
