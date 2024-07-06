from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import LoginManager, current_user

db = SQLAlchemy()
DB_NAME = "database.db"
DB_PATH="website/"+DB_NAME


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), DB_NAME)
    print(DATABASE_PATH)
    app.config['SQLALCHEMY_DATABASE_URI'] =f'sqlite:///{DATABASE_PATH}'
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User #todo: import Query?

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    with app.app_context():
        create_database()
        
    return app


def create_database():
    if not os.path.exists('website/' + DB_NAME):
        db.create_all()
        print('Created Database!')
    else:
        print('Database already exists!')
