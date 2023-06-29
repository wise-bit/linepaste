from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:os.getenv('DB_PASSWORD')@localhost:3306/pastes"
db = SQLAlchemy(app)


class Paste(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    title = db.Column(db.String(100))

    # Add other fields like expiration date, visibility settings, etc.
