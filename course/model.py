from auth.model import db,Base
from flask_login import UserMixin

class Course(db.Model,UserMixin):
    __tablename__ = 'course'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Integer, nullable = True)
    name = db.Column(db.String(255), nullable=True)
    openai_key = db.Column(db.String(500), nullable=True)
    stripe_api_key = db.Column(db.String(255), nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('adminuser.id'))
    users = db.relationship('User', backref='subscribers')
    url = db.Column(db.String(500), nullable = True)
    color = db.Column(db.String(50), nullable = True)
    title = db.Column(db.String(100), nullable = True)
    price = db.Column(db.Float(6,2), nullable = True)
    courselink = db.Column(db.String(200), nullable = True)
    sender_email = db.Column(db.String(200), nullable = True)
    sender_password = db.Column(db.String(200), nullable = True)
    product_id = db.Column(db.String(255), nullable=True)
    endpoint_secret = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"<compain(name='{self.name}'"

