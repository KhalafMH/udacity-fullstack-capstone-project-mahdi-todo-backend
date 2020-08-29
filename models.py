import os
from typing import cast

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

from constants import DEFAULT_DATABASE_URL

DATABASE_URL = os.environ.get('DATABASE_URL') or DEFAULT_DATABASE_URL

db = SQLAlchemy()


def setup_db(app, database_url=DATABASE_URL):
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    return db


class User(db.Model):
    __tablename__ = 'users'

    def __init__(self, name, email):
        self.name = name
        self.email = email

    def __eq__(self, o: object) -> bool:
        if type(o) == type(self):
            o_user: User = cast(User, o)
            return self.name == o_user.name \
                   and self.email == o_user.email \
                   and self.id == o_user.id
        else:
            return False

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    todos = db.relationship('Todo', backref='user')

    def persist(self):
        """
        Inserts this `User` into the `users` database table.

        :return: A clone of this user containing the `id` of the inserted record.
        """
        try:
            db.session.add(self)
            db.session.commit()
            return self.clone()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e
        finally:
            db.session.close()

    def delete(self):
        """
        Deletes this `User` from the database table.

        :return: True when the deletion is successful
        """
        try:
            user = User.query.get(self.id)
            db.session.delete(user)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e
        finally:
            db.session.close()

    @property
    def json(self):
        """
        Helper for getting the short JSON representation of the user without the todos.

        :return: A dictionary with the short representation of the user.
        """
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email
        }

    @property
    def json_full(self):
        """
        Helper for getting the full JSON representation of the user with all the todos.

        :return: A dictionary with the long representation of the user.
        """
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "todos": list(map(lambda x: x.json, self.todos))
        }

    def clone(self):
        """
        Clones this user object.

        :return: A new `User` object with the same properties as this one
        """
        result = User(name=self.name, email=self.email)
        result.id = self.id
        return result


class Todo(db.Model):
    __tablename__ = 'todos'

    def __init__(self, title, done):
        self.title = title
        self.done = done

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String, nullable=False)
    done = db.Column(db.Boolean, nullable=False)

    # user = backref from User class

    @property
    def json(self):
        """
        Helper for getting the JSON representation of the todo.

        :return: A dictionary with the JSON representation of the todo.
        """
        return {
            "id": self.id,
            "title": self.title,
            "done": self.done
        }
