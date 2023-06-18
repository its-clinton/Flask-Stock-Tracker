from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from  flask_security import UserMixin
from flask import *

app = Flask(__name__)

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(255), unique=False, nullable=False)
    active = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return '<User %r>' % self.email
        
# admin view
admin = Admin(app)
admin.add_view(ModelView(User, db.session))