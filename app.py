from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from dotenv import load_dotenv
from datetime import datetime
import os


app = Flask(__name__)
app.debug = True

load_dotenv()

app = Flask(__name__)
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"mysql://sat:{os.getenv('DB_PASSWORD')}@127.0.0.1:3306/pastes"
db = SQLAlchemy(app)


class Paste(db.Model):
    __tablename__ = "user_pastes"
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String)
    title = db.Column(db.String(100))
    contents = db.Column(db.Text)
    passwd = db.Column(db.String(30))


@app.route("/")
def home():
    user_agent = request.headers.get("User-Agent")
    print(f"{user_agent}\n----------")

    return render_template("title_page.html")


@app.route("/create", methods=["GET", "POST"])
def create_paste():
    print(get_last_id())
    print("----------")

    if request.method == "POST":
        # Process form data and create a new paste and save the paste to the database
        # Assuming the newly created paste has an ID assigned
        new_id = get_last_id() + 1

        content = request.form.get("content")
        title = request.form.get("title")
        passwd = request.form.get("passwd")

        unique_id = f"{datetime.now().strftime('%y%m%d')}{new_id}"

        user_pastes = Paste(
            uuid=unique_id, contents=content, title=title, passwd=passwd
        )
        db.session.add(user_pastes)
        db.session.commit()

        return redirect(f"/p/{unique_id}")  # Redirect to the view page of the paste

    else:
        return render_template("create_paste.html")


@app.route("/p/<paste_id>")
def view_paste(paste_id):
    # Retrieve the paste from the database using the paste_id
    # Return the paste content and other details
    paste = Paste.query.filter(Paste.uuid == paste_id).first()
    if paste is None:
        # Handle paste not found scenario
        return render_template('paste_not_found.html')

    return render_template('view_paste.html', paste=paste)


# Fetch the last ID used
def get_last_id():
    return (db.session.query(Paste.id).order_by(Paste.id.desc()).first() or (0,))[0]


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)  # ssl_context='adhoc'

