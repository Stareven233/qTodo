from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api


db = SQLAlchemy()
api = Api()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    # api.init_app(app)
    # api.add_resource(TodoAPI, '/t odo/api/v1')
    from .api_v1 import v1  # 不能在db初始化前，因为v1有用到db
    app.register_blueprint(v1, url_prefix='/api/v1')
    return app


def create_db_table(app):
    with app.app_context():
        db.create_all()


# from app import db
# from app.models import User
# def update_db():
#     with app.app_context():
#         users = User.query.all()
#         for u in users:
#             u.hash_password(u.username)
#             db.session.add(u)
#         db.session.commit()
