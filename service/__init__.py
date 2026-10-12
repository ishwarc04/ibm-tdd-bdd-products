"""Product Management Flask application."""
import os
from flask import Flask
from service.models import db
app = Flask(__name__)
app.config.update(
    SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URI", "sqlite:///products.db"),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)
db.init_app(app)
from service import routes  # noqa: E402,F401
with app.app_context():
    db.create_all()
