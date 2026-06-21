from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import secrets

db = SQLAlchemy()

class User(UserMixin, db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    is_admin = db.Column(
      db.Boolean,
      default=False
    )


class File(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    filename = db.Column(
        db.String(255),
        nullable=False
    )

    s3_key = db.Column(
        db.String(500),
        nullable=False
    )

    filesize = db.Column(
        db.Integer
    )

    upload_date = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id')
    )

    share_token = db.Column(
       db.String(100),
       unique=True,
       nullable=True
    )

    version = db.Column(
      db.Integer,
      default=1
    )

    original_filename = db.Column(
      db.String(255)
    )

    share_token = db.Column(
      db.String(100),
      unique=True,
      nullable=True
    )


class Activity(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    action = db.Column(
        db.String(100)
    )

    filename = db.Column(
        db.String(300)
    )

    timestamp = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    ) 

    user = db.relationship('User', backref='activities')   