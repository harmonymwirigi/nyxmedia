from flask import Flask
from auth.route import auth_bp
from user.route import user_bp
from course.route import courses
from auth.model import db, User, Adminuser
from course.model import Course
from emails.models import EmailTemplate
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
import os
import logging
from logging.handlers import RotatingFileHandler
import stripe
from sqlalchemy.exc import OperationalError
from flask_migrate import Migrate  # Import Flask-Migrate

# Initialize the Flask app
app = Flask(__name__)

# Ensure the instance folder exists
os.makedirs(app.instance_path, exist_ok=True)

# Configuration
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://tonirodriguez:Harmo36840568@tonirodriguez.mysql.pythonanywhere-services.com/tonirodriguez$course'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# User loader function required by Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return Adminuser.query.filter_by(id=user_id).first()

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Initialize Flask extensions within app context
with app.app_context():
    db.init_app(app)

    # Ensure the connection is pre-pinged to prevent disconnections
    engine = db.get_engine()
    engine.dispose()  # Dispose of previous connections
    engine.pool._use_threadlocal = True
    engine.pool._pre_ping = True

    db.create_all()  # Create database tables for our models



# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(user_bp, url_prefix='/users')
app.register_blueprint(courses, url_prefix='/compaign')

# Logging setup
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/nyxmedia.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Nyx Media startup')

# Handle teardown and exceptions
@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()

@app.errorhandler(OperationalError)
def handle_db_error(error):
    return "Database connection error.....", 500

# Run the Flask app
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)
