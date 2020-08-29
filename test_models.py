import unittest

from app import app
from constants import TEST_DATABASE_URL
from models import setup_db, User, Todo


class ModelTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app = app
        self.client = app.test_client()
        self.db = setup_db(self.app, TEST_DATABASE_URL)

        with self.app.app_context():
            self.db.engine.execute('''
                DROP TABLE IF EXISTS todos;
                DROP TABLE IF EXISTS users;
            ''')
            self.db.create_all()

    def tearDown(self) -> None:
        self.db.session.close()

    def test_user_persist_persists_the_user_to_the_database(self):
        test_name = 'Example User'
        test_email = 'user@example.com'

        # Given: User not present in database
        count = User.query.filter_by(email=test_email).count()
        self.assertEqual(0, count)

        # When: persist() is called on the user
        user = User(name=test_name, email=test_email)
        persisted_user = user.persist()

        # Then: A record is created in the database table for the user
        user_from_database = User.query.filter_by(email=test_email).one()
        self.assertEqual(test_name, user_from_database.name)
        self.assertEqual(test_email, user_from_database.email)
        self.assertEqual(test_name, persisted_user.name)
        self.assertEqual(test_email, persisted_user.email)
        self.assertEqual(user_from_database.id, persisted_user.id)

    def test_user_json_property(self):
        # Given: A sample user
        user = User(name='Example User', email='user@example.com')
        user.id = '200'

        # When: The `json` property is called
        json = user.json

        # Then: It returns a dictionary with the user details without any todos
        self.assertEqual(user.name, json['name'])
        self.assertEqual(user.email, json['email'])
        self.assertEqual(user.id, json['id'])
        self.assertIsNone(json.get('todos'))
        self.assertEqual(3, len(json))

    def test_user_json_full_property(self):
        # Given: A sample user
        user = User(name='Example User', email='user@example.com')
        user.id = '200'

        # When: The `json` property is called
        json = user.json_full

        # Then: It returns a dictionary with the user details without any todos
        self.assertEqual(user.name, json['name'])
        self.assertEqual(user.email, json['email'])
        self.assertEqual(user.id, json['id'])
        self.assertEqual([], json['todos'])
        self.assertEqual(4, len(json))

    def test_user_clone_returns_identical_object(self):
        # Given: A sample user object
        user = User(name='Example User', email='user@example.com')
        user.id = 200

        # When: The clone method is called
        clone = user.clone()

        # Then: The clone is a different object with the same properties
        self.assertFalse(clone is user, msg='Clone must not be the same object as the original')
        self.assertEqual(dir(clone), dir(user))
        self.assertEqual(clone.name, user.name)
        self.assertEqual(clone.email, user.email)
        self.assertEqual(clone.id, user.id)

    def test_todo_persist_persists_the_todo_in_the_database(self):
        test_title = 'Do something'
        test_done = False

        # Given: User with no todos in the database
        user = User(name='Example User', email='user@example.com')
        user.persist()
        user_before = User.query.get(user.id)
        todos_before = user_before.todos
        self.assertEqual([], todos_before)

        # When: persist() is called on a todo
        todo = Todo(owner_id=user.id, title=test_title, done=test_done)
        todo.persist()

        # Then: A record is created in the database table for the todo
        user_after = User.query.get(user.id)
        self.assertEqual(1, len(user_after.todos))
        self.assertEqual(test_title, user_after.todos[0].title)
        self.assertEqual(test_done, user_after.todos[0].done)

    def test_todo_clone_returns_identical_object(self):
        # Given: A sample todo object
        todo = Todo(owner_id=200, title='Do something', done=False)
        todo.id = 200

        # When: The clone method is called
        clone = todo.clone()

        # Then: The clone is a different object with the same properties
        self.assertFalse(clone is todo, msg='Clone must not be the same object as the original')
        self.assertEqual(dir(clone), dir(todo))
        self.assertEqual(clone.title, todo.title)
        self.assertEqual(clone.done, todo.done)
        self.assertEqual(clone.id, todo.id)
        self.assertEqual(clone.owner_id, todo.owner_id)

    def test_todo_json_property(self):
        # Given: A sample todo
        user = User(name='Example User', email='user@example.com')
        user_before = user.persist()
        todo = Todo(owner_id=user_before.id, title='Do something', done=False)
        todo.id = '200'

        # When: The `json` property is called
        json = todo.json

        # Then: It returns a dictionary with the todo details
        self.assertEqual(todo.title, json['title'])
        self.assertEqual(todo.done, json['done'])
        self.assertEqual(todo.id, json['id'])
        self.assertEqual(todo.owner_id, json['owner_id'])
        self.assertEqual(4, len(json))

    def test_user_delete(self):
        # Given: A user object which is persisted to the database
        user = User(name='Example User', email='user@example.com')
        user_before = user.persist()

        # When: The delete method is called
        result = user_before.delete()

        # Then: The user record is removed from the database
        self.assertEqual(True, result)
        user_after = User.query.get(user_before.id)
        self.assertIsNone(user_after)
