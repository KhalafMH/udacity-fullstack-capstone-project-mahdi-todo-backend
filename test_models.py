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
        pass

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

    def test_todo_json_property(self):
        # Given: A sample todo
        todo = Todo(title='Do something', done=False)
        todo.id = '200'

        # When: The `json` property is called
        json = todo.json

        # Then: It returns a dictionary with the todo details
        self.assertEqual(todo.title, json['title'])
        self.assertEqual(todo.done, json['done'])
        self.assertEqual(todo.id, json['id'])
        self.assertEqual(3, len(json))
