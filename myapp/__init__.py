from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_migrate import Migrate

db = SQLAlchemy()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)

    Migrate(app, db)

    from myapp import models

    from myapp.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from myapp.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    from myapp.main import main_bp
    app.register_blueprint(main_bp, url_prefix='/')

    from myapp.query import query_bp
    app.register_blueprint(query_bp, url_prefix='/query')

    from myapp.predict import predict_bp
    app.register_blueprint(predict_bp, url_prefix='/predict')

    from myapp.parking import parking_bp
    app.register_blueprint(parking_bp, url_prefix='/parking')

    return app
