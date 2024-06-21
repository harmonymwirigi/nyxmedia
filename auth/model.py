from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import declarative_base
import stripe
from werkzeug.security import check_password_hash

Base  = declarative_base()

db = SQLAlchemy()

class Adminuser(db.Model, Base):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80),nullable=True)
    course = db.relationship('Course', backref='my_coure')
    template = db.relationship('EmailTemplate', backref='my_templates')
    password = db.Column(db.String(128), nullable=True)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return self.id
    def is_active(self):
        return True
    def is_authenticated(self):
        return True
    def get_id(self):
        return self.id

class User(db.Model,Base):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    customer_id = db.Column(db.String(200), nullable = True)
    payment_intent_id = db.Column(db.String(200), nullable = True)
    amount = db.Column(db.String(200), nullable=True)
    status = db.Column(db.Integer, nullable= True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))


    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return self.id
    def is_active(self):
        return True
    def is_authenticated(self):
        return True
    def get_id(self):
        return self.id



