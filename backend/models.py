import mongoengine as me
from flask_security import UserMixin

# Connect to MongoDB directly
def init_db(app):
    me.connect(host=app.config['MONGODB_HOST'])


class User(me.Document, UserMixin):
    email = me.StringField(max_length=255, unique=True)
    username = me.StringField(max_length=255, unique=True)
    password = me.StringField(max_length=255)
    active = me.BooleanField(default=True)
    fs_uniquifier = me.StringField(max_length=64, unique=True)
    confirmed_at = me.DateTimeField()
    roles = me.ListField(me.StringField(), default=[]) # Dummy field for Flask-Security
