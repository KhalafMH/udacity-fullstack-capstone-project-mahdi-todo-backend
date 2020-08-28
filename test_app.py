import unittest

from app import app
from models import setup_db, User

TEST_DATABASE_URL = 'postgres://postgres:password@localhost:5432/mahdi_todo_test'


class AppTest(unittest.TestCase):
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

    def test_post_user_persists_user(self):
        test_name = 'Example User'
        test_email = 'user@example.com'
        user_count = User.query.filter_by(email=test_email).count()
        self.assertEqual(0, user_count)
        response = self.client.post('/api/v1/users', json={'name': test_name, 'email': test_email})
        self.assertEqual(201, response.status_code)
        self.assertEqual(test_name, response.json['user']['name'])
        self.assertEqual(test_email, response.json['user']['email'])
        user = User.query.filter_by(email=test_email).one()
        self.assertEqual(test_name, user.name)