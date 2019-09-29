# Authors: Tessa Pham & Zainab Batool

from flask import Flask, request
from flask_mail import Mail
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_uploads import UploadSet, IMAGES, configure_uploads
from flask_babel import Babel

UPLOAD_FOLDER = 'static/uploads'
UPLOADS_DEFAULT_DEST = 'static/uploads'
UPLOADS_DEFAULT_URL = 'http://localhost:5000/static/img/'
UPLOADED_IMAGES_URL = 'http://localhost:5000/static/img/'

app = Flask(__name__, static_url_path='/static')
app.config.from_object(Config)
app.config['UPLOADS_DEFAULT_DEST'] = UPLOADS_DEFAULT_DEST
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.jinja_env.filters['zip'] = zip
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
images = UploadSet('images', IMAGES)
configure_uploads(app, images)
babel = Babel(app)
mail = Mail(app)

from app import routes, models
@babel.localeselector
def get_locale():
    return 'en'