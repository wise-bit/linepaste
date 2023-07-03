from waitress import serve
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from dotenv import load_dotenv
from datetime import datetime
import bcrypt
import os


app = Flask(__name__)
app.debug = True

load_dotenv()

app = Flask(__name__)
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"mysql://sat:{os.getenv('DB_PASSWORD')}@127.0.0.1:3306/pastes"
db = SQLAlchemy(app)

encrypt_salt = b'$2b$12$wBaDKOH6MeU8qZFd10JjT.'

def hash(original: str) -> str:
    return bcrypt.hashpw(original.encode(), encrypt_salt) 


class Paste(db.Model):
    __tablename__ = "user_pastes"
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String)
    title = db.Column(db.String(100))
    contents = db.Column(db.Text)
    passwd = db.Column(db.String(30))


@app.route("/")
def home():
    # user_agent = request.headers.get("User-Agent")
    # print(f"{user_agent}\n----------")
    
    return render_template("title_page.html")


@app.route("/create", methods=["GET", "POST"])
def create_paste():
    if request.method == "POST":
        # Process form data and create a new paste and save the paste to the database
        # Assuming the newly created paste has an ID assigned
        new_id = get_last_id() + 1

        content = request.form.get("content")
        title = request.form.get("title")
        passwd = hash(request.form.get("passwd"))

        unique_id = f"{datetime.now().strftime('%y%m%d')}{new_id}"

        user_pastes = Paste(
            uuid=unique_id, contents=content, title=title, passwd=passwd
        )
        db.session.add(user_pastes)
        db.session.commit()

        return redirect(f"/p/{unique_id}")  # Redirect to the view page of the paste

    else:
        return render_template("create_paste.html")


@app.route('/p/<paste_id>', methods=['GET', 'POST'])
def view_paste(paste_id):
    # Retrieve the paste from the database using the paste_id
    # Return the paste content and other details
    paste_pass = Paste.query.with_entities(Paste.passwd).filter(Paste.uuid == paste_id).first()

    if paste_pass:
        if paste_pass[0]:
            if request.method == 'POST':
                entered_password = request.form.get('passwd')
                
                if hash(entered_password).decode() == paste_pass[0]:
                    # Correct password entered, retrieve the full paste data
                    paste = Paste.query.filter(Paste.uuid == paste_id).first()
                    return render_template("view_paste.html", paste=paste)

                # Incorrect password entered, show an error message
                error_message = "Incorrect password, please try again!"
                return render_template('password_input.html', paste_id=paste_id, error=error_message)

            # Display password input form for password-protected paste
            return render_template('password_input.html')

        # No password set, display the paste content
        paste = Paste.query.filter(Paste.uuid == paste_id).first()
        return render_template("view_paste.html", paste=paste)

    return render_template("paste_not_found.html")


# Fetch the last ID used
def get_last_id():
    return (db.session.query(Paste.id).order_by(Paste.id.desc()).first() or (0,))[0]


if __name__ == "__main__":
    # app.run(host='0.0.0.0', port=5000)  # ssl_context='adhoc'
    serve(app, host="0.0.0.0", port=8080)
