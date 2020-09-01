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

    def test_get_all_users_returns_all_users(self):
        # Given: Two users exist in the database
        user1 = User(name='Example 1', email='user1@example.com')
        user2 = User(name='Example 2', email='user2@example.com')
        user_1_before = user1.persist()
        user_2_before = user2.persist()

        # When: A request is made to the get all users endpoint
        response = self.client.get(f'{BASE_URL}/users')

        # Then: The response is successful and contains the details of the two users
        self.assertEqual(200, response.status_code)
        self.assertTrue(response.json['success'])
        self.assertTrue(user_1_before.json in response.json['users'])
        self.assertTrue(user_2_before.json in response.json['users'])

    def test_get_all_users_returns_success_with_empty_list_when_no_users_in_database(self):
        # Given: No users are in the database
        users = User.query.all()
        self.assertEqual([], users)

        # When: A request is made to the get all users endpoint
        response = self.client.get(f'{BASE_URL}/users')

        # Then: The response is successful with an empty list of users
        self.assertEqual(200, response.status_code)
        self.assertTrue(response.json['success'])
        self.assertEqual([], response.json['users'])

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
        self.assertFalse(response.json["success"])

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
        self.assertFalse(response.json["success"])
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
        self.assertFalse(response1.json["success"])
        self.assertFalse(response2.json["success"])
        self.assertEqual(user_before, User.query.get(user_before.id))

    def test_patch_user_fails_with_415_when_request_is_not_json(self):
        # Given: A record exists in the database
        user = User(name='Example User', email='user@example.com')
        user_before = user.persist()

        # When: A request is performed with no JSON content
        response = self.client.patch(f'{BASE_URL}/users/{user_before.id}', data='Hello There')

        # Then: A 415 error is received
        self.assertEqual(415, response.status_code)
        self.assertFalse(response.json["success"])

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
        self.assertFalse(response.json["success"])

    def test_post_todo_creates_todo_for_a_user(self):
        # Given: No todos are present in the database for a user
        user = User(name='Example User', email='user@example.com')
        user_before = user.persist()

        todo_title1 = 'Do something'
        todo_title2 = 'Do something else'
        count_todo_before1 = Todo.query.filter_by(title=todo_title1).count()
        count_todo_before2 = Todo.query.filter_by(title=todo_title2).count()
        self.assertEqual(0, count_todo_before1)
        self.assertEqual(0, count_todo_before2)

        # When: A request is made to the POST endpoint for creating todos
        todos = [
            {'title': todo_title1, 'done': False},
            {'title': todo_title2, 'done': True}
        ]
        response = self.client.post(f'{BASE_URL}/users/{user_before.id}/todos', json=todos)

        self.assertEqual(200, response.status_code)
        self.assertTrue(response.json['success'])
        mapped_response_todos = list(map(lambda x: {'title': x['title'], 'done': x['done']}, response.json['todos']))
        self.assertEqual(todos, mapped_response_todos)
        self.assertEqual(user_before.id, response.json['user_id'])

    def test_post_todo_fails_with_404_when_user_non_existent(self):
        ID = 2000

        # Given: No user exists with id ID in the database
        user = User.query.get(ID)
        self.assertIsNone(user)

        todo = {'title': 'Do something', 'done': False}

        # When: A post request is made to create todos for user with id ID
        response = self.client.post(f'{BASE_URL}/users/{ID}/todos', json=[todo])

        # Then: A failed response with error 404 is received
        self.assertEqual(404, response.status_code)
        self.assertFalse(response.json["success"])

    def test_post_todo_fails_with_415_when_data_not_json(self):
        # Given: A user exists in the database
        user = User(name='Example User', email='user@example.com')
        user_before = user.persist()

        # When: A request is made to create a todo with no JSON content
        response = self.client.post(f'{BASE_URL}/users/{user_before.id}/todos')

        # Then: A failed response with error 415 is received
        self.assertEqual(415, response.status_code)
        self.assertFalse(response.json["success"])

    def test_post_todo_fails_with_400_when_request_invalid(self):
        # Given: A user exists in the database
        user = User(name='Example User', email='user@example.com')
        user_before = user.persist()

        # When: A post request is made to the create todos endpoint with no title for a todo
        todo = {'done': True}
        response1 = self.client.post(f'{BASE_URL}/users/{user_before.id}/todos', json=[todo])
        response2 = self.client.post(f'{BASE_URL}/users/{user_before.id}/todos', json=[])
        response3 = self.client.post(f'{BASE_URL}/users/{user_before.id}/todos', json='Do something')

        # Then: A 400 response is received
        self.assertEqual(400, response1.status_code)
        self.assertEqual(400, response2.status_code)
        self.assertEqual(400, response3.status_code)

    def test_get_user_todos_returns_the_todos(self):
        # Given: A user with some todos
        user = User(name='Example User', email='user@example.com')
        user_before = user.persist()
        todo1 = Todo(owner_id=user_before.id, title='Do something', done=True)
        todo2 = Todo(owner_id=user_before.id, title='Do something else', done=False)
        todo1_clone = todo1.persist()
        todo2_clone = todo2.persist()
        persisted_user = User.query.get(user_before.id)
        self.assertEqual(2, len(persisted_user.todos))

        # When: A request is made to the get user todos endpoint
        response = self.client.get(f'{BASE_URL}/users/{user_before.id}/todos')

        # Then: The request is successful and the response contains the user's todos
        self.assertEqual(200, response.status_code)
        self.assertTrue(response.json['success'])
        self.assertEqual(user_before.id, response.json['user_id'])
        self.assertEqual([todo1_clone.json, todo2_clone.json], response.json['todos'])

    def test_get_user_todos_fails_with_404_when_user_non_existent(self):
        ID = 2000

        # Given: No user exists with id ID in the database
        user = User.query.get(ID)
        self.assertIsNone(user)

        # When: A get request is made to get todos for user with id ID
        response = self.client.get(f'{BASE_URL}/users/{ID}/todos')

        # Then: A failed response with error 404 is received
        self.assertEqual(404, response.status_code)
        self.assertFalse(response.json["success"])

    def test_patch_todo_modifies_the_todo(self):
        # Given: A user with a single todo
        user = User(name='Example User', email='user@example.com')
        user_before = user.persist()
        todo = Todo(owner_id=user_before.id, title='Do something', done=False)
        todo_before = todo.persist()

        # When: A request is made to modify the todo
        response = self.client.patch(f'{BASE_URL}/users/{user_before.id}/todos/{todo_before.id}', json={'done': True})

        # Then: The response is successful and the todo is modified in the database
        self.assertEqual(200, response.status_code)
        self.assertTrue(response.json['success'])
        self.assertEqual(user_before.id, response.json['user_id'])
        self.assertEqual(todo_before.title, response.json['todo']['title'])
        self.assertEqual(True, response.json['todo']['done'])

    def test_patch_todo_fails_with_404_when_todo_non_existent_for_existing_user(self):
        TODO_ID = 2000

        # Given: No todo exists with id TODO_ID in the database for a user
        todo = Todo.query.get(TODO_ID)
        self.assertIsNone(todo)
        user = User(name='Example User', email='user@example.com')
        user_before = user.persist()

        # When: A patch request is made to modify todo with id TODO_ID
        response = self.client.patch(f'{BASE_URL}/users/{user_before.id}/todos/{TODO_ID}', json={'done': True})

        # Then: A failed response with error 404 is received
        self.assertEqual(404, response.status_code)
        self.assertFalse(response.json["success"])

    def test_patch_todo_fails_with_400_when_request_invalid(self):
        # Given: A user exists in the database with one todo
        user = User(name='Example User', email='user@example.com')
        user_before = user.persist()
        todo = Todo(owner_id=user_before.id, title='Do something', done=False)
        todo_before = todo.persist()

        # When: An invalid patch request is made to the modify todo endpoint
        response1 = self.client.patch(f'{BASE_URL}/users/{user_before.id}/todos/{todo_before.id}', json={})
        response2 = self.client.patch(f'{BASE_URL}/users/{user_before.id}/todos/{todo_before.id}', json='')

        # Then: A 400 response is received
        self.assertEqual(400, response1.status_code)
        self.assertEqual(400, response2.status_code)
        self.assertFalse(response1.json["success"])
        self.assertFalse(response2.json["success"])

    def test_patch_todo_fails_with_415_when_data_not_json(self):
        # Given: A user exists in the database with one todo
        user = User(name='Example User', email='user@example.com')
        user_before = user.persist()
        todo = Todo(owner_id=user_before.id, title='Do something', done=False)
        todo_before = todo.persist()

        # When: A request is made to modify the todo with no JSON content
        response = self.client.patch(f'{BASE_URL}/users/{user_before.id}/todos/{todo_before.id}')

        # Then: A failed response with error 415 is received
        self.assertEqual(415, response.status_code)
        self.assertFalse(response.json["success"])

    def test_delete_todo_deletes_the_todo_from_the_database(self):
        # Given: A user exists in the database with one todo
        user = User(name='Example User', email='user@example.com')
        user_before = user.persist()
        todo = Todo(owner_id=user_before.id, title='Do something', done=False)
        todo_before = todo.persist()

        # When: A delete request is performed
        response = self.client.delete(f'{BASE_URL}/users/{user_before.id}/todos/{todo_before.id}')

        # Then: The todo record is deleted from the database
        self.assertEqual(200, response.status_code)
        todo_after = Todo.query.get(todo_before.id)
        self.assertIsNone(todo_after)
        self.assertEqual(True, response.json['success'])

    def test_delete_todo_fails_with_404_when_todo_non_existent(self):
        TODO_ID = 2000

        # Given: No todo exists with id TODO_ID in the database for a user
        user = User(name='Example User', email='user@example.com')
        user_before = user.persist()
        todo = Todo.query.get(TODO_ID)
        self.assertIsNone(todo)

        # When: A delete request is performed for deleting todo with id TODO_ID
        response = self.client.delete(f'{BASE_URL}/users/{user_before.id}/todos/{TODO_ID}')

        # Then: A failed response with error 404 is received
        self.assertEqual(404, response.status_code)
        self.assertFalse(response.json["success"])
