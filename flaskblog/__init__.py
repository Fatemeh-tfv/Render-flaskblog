from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flaskblog.config import config
from flask_wtf.csrf import generate_csrf

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
mail = Mail()


def create_app(config_class= config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config)
    app.config['PROPAGATE_EXCEPTIONS'] = True

    @app.context_processor
    def inject_csrf():
        # makes csrf_token() available in all templates
        return dict(csrf_token=generate_csrf)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from flaskblog.users.routs import users
    from flaskblog.admin.routes import admin
    from flaskblog.posts.routs import posts
    from flaskblog.main.routs import main
    from flaskblog.errors.handlers import errors

    app.register_blueprint(users)
    app.register_blueprint(admin)
    app.register_blueprint(posts)
    app.register_blueprint(main)
    app.register_blueprint(errors)

    return app