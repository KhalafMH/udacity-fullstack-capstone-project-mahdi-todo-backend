import unittest

from app import app
from constants import TEST_DATABASE_URL
from models import setup_db, User, Todo

BASE_URL = '/api/v1'


class AppTest(unittest.TestCase):
    def setUp(self) -> None:
        self.app = app
        self.client = app.test_client()
        self.db = setup_db(self.app, TEST_DATABASE_URL)

        with self.app.app_context():
            self.db.engine.execute(f'''
                DROP TABLE IF EXISTS {Todo.__tablename__};
                DROP TABLE IF EXISTS {User.__tablename__};
            ''')
            self.db.create_all()

    def tearDown(self) -> None:
        self.db.session.close()

    def test_post_user_persists_user(self):
        test_name = 'Example User'
        test_email = 'user@example.com'

        # Given: User not present in database
        user_count = User.query.filter_by(email=test_email).count()
        self.assertEqual(0, user_count)

        # When: POST user request performed
        response = self.client.post(f'{BASE_URL}/users', json={'name': test_name, 'email': test_email})

        # Then: Request is successful and user is present in database
        self.assertEqual(201, response.status_code)
        self.assertEqual(test_name, response.json['user']['name'])
        self.assertEqual(test_email, response.json['user']['email'])
        user = User.query.filter_by(email=test_email).one()
        self.assertEqual(test_name, user.name)

    def test_get_user_returns_user(self):
        # Given: A user exists in the database
        user = User(name='Example User', email='user@example.com')
        user_before = user.persist()

        # When: A request is performed to the GET user endpoint
        response = self.client.get(f'{BASE_URL}/users/{user_before.id}')

        # Then: The response is successful and contains details of the user
        self.assertEqual(200, response.status_code)
        self.assertTrue(response.json['success'])
        self.assertEqual(user_before.name, response.json['user']['name'])
        self.assertEqual(user_before.email, response.json['user']['email'])
        self.assertEqual(user_before.id, response.json['user']['id'])

    def test_get_user_fails_with_404_when_user_non_existent(self):
        ID = 2000

        # Given: No user exists with id ID in the database
        user = User.query.get(ID)
        self.assertIsNone(user)

        # When: A get request is performed for getting the user with id ID
        response = self.client.get(f'{BASE_URL}/users/{ID}')

        # Then: A failed response with error 404 is received
        self.assertEqual(404, response.status_code)

    def test_patch_user_modifies_the_user_record(self):
        old_name = 'Example User'
        new_name = 'Sample User'
        old_email = 'user@example.com'
        new_email = 'sample@example.com'

        # Given: A user exists in the database
        user = User(name=old_name, email=old_email)
        user_before = user.persist()

        # When: The patch user endpoint is called
        first_response = self.client.patch(f'{BASE_URL}/users/{user_before.id}', json={'name': new_name})
        second_response = self.client.patch(f'{BASE_URL}/users/{user_before.id}', json={'email': new_email})

        # Then: The user record in the database is modified
        user_after = User.query.get(user_before.id)
        self.assertEqual(new_name, user_after.name)
        self.assertEqual(new_email, user_after.email)
        self.assertEqual(200, first_response.status_code)
        self.assertEqual(new_name, first_response.json['user']['name'])
        self.assertEqual(old_email, first_response.json['user']['email'])
        self.assertEqual(new_name, second_response.json['user']['name'])
        self.assertEqual(new_email, second_response.json['user']['email'])

    def test_patch_user_fails_with_404_when_user_non_existent(self):
        ID = 2000

        # Given: No user exists with id ID in the database
        user = User.query.get(ID)
        self.assertIsNone(user)

        # When: A patch request is performed for modifying user with id ID
        response = self.client.patch(f'{BASE_URL}/users/{ID}', json={'name': 'New Name'})

        # Then: A failed response with error 404 is received and user is not inserted in the database
        self.assertEqual(404, response.status_code)
        self.assertIsNone(User.query.get(ID))

    def test_patch_user_fails_with_400_when_request_invalid(self):
        # Given: A user exists in the database
        user = User(name='Example User', email='user@example.com')
        user_before = user.persist()

        # When: A request is made to modify the user with invalid data
        response1 = self.client.patch(f'{BASE_URL}/users/{user_before.id}', json={'email': 'My Email'})
        response2 = self.client.patch(f'{BASE_URL}/users/{user_before.id}', json={})

        # Then: A failed response with error 400 is received and user is not modified
        self.assertEqual(400, response1.status_code)
        self.assertEqual(400, response2.status_code)
        self.assertEqual(user_before, User.query.get(user_before.id))

    def test_patch_user_fails_with_415_when_request_is_not_json(self):
        # Given: A record exists in the database
        user = User(name='Example User', email='user@example.com')
        user_before = user.persist()

        # When: A request is performed with no JSON content
        response = self.client.patch(f'{BASE_URL}/users/{user_before.id}', data='Hello There')

        # Then: A 415 error is received
        self.assertEqual(415, response.status_code)

    def test_delete_user_deletes_the_user_from_the_database(self):
        # Given: A user exists in the database
        user = User(name='Example User', email='user@example.com')
        user_before = user.persist()

        # When: A delete request is performed
        response = self.client.delete(f'{BASE_URL}/users/{user_before.id}')

        # Then: The user record is deleted from the database
        self.assertEqual(200, response.status_code)
        user_after = User.query.get(user_before.id)
        self.assertIsNone(user_after)
        self.assertEqual(True, response.json['success'])

    def test_delete_user_fails_with_404_when_user_non_existent(self):
        ID = 2000

        # Given: No user exists with id ID in the database
        user = User.query.get(ID)
        self.assertIsNone(user)

        # When: A delete request is performed for deleting user with id ID
        response = self.client.delete(f'{BASE_URL}/users/{ID}')

        # Then: A failed response with error 404 is received
        self.assertEqual(404, response.status_code)
