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
import sshtunnel
from flask_migrate import Migrate



# Initialize the Flask app
app = Flask(__name__)
admin = Admin()

migrate = Migrate(app, db)

# Set up the SSH tunnel
tunnel = sshtunnel.SSHTunnelForwarder(
    ('ssh.pythonanywhere.com'), 
    ssh_username='tonirodriguez',
    ssh_password='QN&%Y4_TfVvd$&2',
    remote_bind_address=('tonirodriguez.mysql.pythonanywhere-services.com', 3306)
)

# Start the SSH tunnel
tunnel.start()

# Ensure the instance folder exists
os.makedirs(app.instance_path, exist_ok=True)

# Configuration
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://tonirodriguez:Harmo36840568@127.0.0.1:{tunnel.local_bind_port}/tonirodriguez$course'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize CSRF Protection
# csrf = CSRFProtect(app) # Uncomment if CSRF protection is needed

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# User loader function required by Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return Adminuser.query.filter_by(id=user_id).first()

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

# Run the Flask app
if __name__ == "__main__":
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    finally:
        tunnel.stop()
