from flask import Flask
from auth.route import auth_bp
from user.route import user_bp
from course.route import courses
from auth.model import db, User, Adminuser
from course.model import Course
from flask_admin import Admin
from emails.models import EmailTemplate
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
import os
import logging
from logging.handlers import RotatingFileHandler
import stripe

# Initialize the Flask app
app = Flask(__name__)
admin = Admin()

# Ensure the instance folder exists
os.makedirs(app.instance_path, exist_ok=True)

# Configuration
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://admin:Harmo36840568@database-1.c1oku62s0o5m.ap-south-1.rds.amazonaws.com/nyxmedia'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# User loader function required by Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return Adminuser.query.get(int(user_id))

# Initialize Flask extensions within app context
# Initialize Flask extensions within app context
with app.app_context():
    db.init_app(app)
    db.create_all()  # Create database tables for our models
    
    admin.init_app(app)
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(EmailTemplate, db.session))
    admin.add_view(ModelView(Course, db.session))

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(user_bp, url_prefix='/users')
app.register_blueprint(courses, url_prefix='/compaign')

# Logging setup
handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=3)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)

# Run the Flask app
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
