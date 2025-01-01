from flask import Flask
from flask_mail import Mail
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect  # Import CSRFProtect
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__, static_url_path='/static', static_folder='static')
csrf = CSRFProtect()

# Configure Flask app
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
csrf.init_app(app)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = 'PoIu1234@'
app.config['MAIL_DEFAULT_SENDER'] = 'gg2maintenance@gmail.com'

mail = Mail(app)

# Register the blueprint
from app.routes import bp
app.register_blueprint(bp, url_prefix='/')

# Create the app instance
def create_app():
    return app
