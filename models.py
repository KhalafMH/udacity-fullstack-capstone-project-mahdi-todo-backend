import os

from flask_sqlalchemy import SQLAlchemy

DATABASE_URL = os.environ.get('DATABASE_URL') or 'postgres://postgres:password@localhost:5432/mahdi_todo'

db = SQLAlchemy()


def setup_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    return db


class User(db.Model):
    __tablename__ = 'users'

    def __init__(self, name, email):
        self.name = name
        self.email = email

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    todos = db.relationship('Todo', backref='user')


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
