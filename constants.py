import os

DEFAULT_DATABASE_URL = 'postgresql://postgres:password@localhost:5432/mahdi_todo'
TEST_DATABASE_URL = os.environ.get('TEST_DATABASE_URL') \
                    or 'postgresql://postgres:password@localhost:5432/mahdi_todo_test'
