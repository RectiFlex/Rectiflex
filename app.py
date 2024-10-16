import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_socketio import SocketIO

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "a secret key"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config['INVENTORY_API_URL'] = os.environ.get('INVENTORY_API_URL', 'https://api.example.com/v1')
app.config['INVENTORY_API_KEY'] = os.environ.get('INVENTORY_API_KEY', 'your-api-key')

db.init_app(app)
migrate = Migrate(app, db)

socketio = SocketIO(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

from routes import *
from external_systems import init_inventory_system

with app.app_context():
    init_inventory_system(app)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
