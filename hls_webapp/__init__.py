from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from hls_webapp.config import Config


db = SQLAlchemy()
bcrypt = Bcrypt()
sess = Session()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
mail = Mail()
from hls_webapp.models import User

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    sess.init_app(app)
    db.init_app(app)

    with app.app_context():
        db.create_all()

    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from hls_webapp.users.routes import users
    from hls_webapp.main.routes import main
    from hls_webapp.errors.handlers import errors
    app.register_blueprint(users)
    app.register_blueprint(main)
    app.register_blueprint(errors)

    return app
