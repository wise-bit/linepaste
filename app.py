from waitress import serve
from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from apscheduler.schedulers.background import BackgroundScheduler

from dotenv import load_dotenv
from datetime import datetime, timedelta
import bcrypt
import os
import atexit


app = Flask(__name__)
app.debug = True

load_dotenv()

app = Flask(__name__)
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"mysql+pymysql://sat:{os.getenv('DB_PASSWORD')}@127.0.0.1:3306/pastes"
db = SQLAlchemy(app)


# Schedule tasks
def delete_expired_pastes():
    with app.app_context():
        current_time = datetime.now()
        expired_pastes = Paste.query.filter(Paste.expire_at < current_time).all()

        for paste in expired_pastes:
            db.session.delete(paste)

        db.session.commit()


scheduler = BackgroundScheduler()
scheduler.add_job(delete_expired_pastes, "interval", seconds=10)
scheduler.start()

atexit.register(lambda: scheduler.shutdown())


encrypt_salt = b"$2b$12$wBaDKOH6MeU8qZFd10JjT."


def hash(original: str) -> str:
    if original:
        return bcrypt.hashpw(original.encode(), encrypt_salt)
    return ""


class Paste(db.Model):
    __tablename__ = "user_pastes"
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String)
    title = db.Column(db.String(100))
    contents = db.Column(db.Text)
    passwd = db.Column(db.String(30))
    created_at = db.Column(db.DateTime, default=datetime.today())
    expire_at = db.Column(db.DateTime, default=datetime.today() + timedelta(minutes=60))


class EspData(db.Model):
    __tablename__ = "mock_sensor_1"
    id = db.Column(db.Integer, primary_key=True)
    value1 = db.Column(db.String(100))
    value2 = db.Column(db.String(100))

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

        lifetime = min(int(request.form.get("expiry") or 60), 2880)
        created_at = datetime.today()
        expire_at = datetime.today() + timedelta(minutes=lifetime)
        unique_id = f"{datetime.now().strftime('%y%m%d')}{new_id}"

        user_pastes = Paste(
            uuid=unique_id,
            contents=content,
            title=title,
            passwd=passwd,
            created_at=created_at,
            expire_at=expire_at,
        )
        db.session.add(user_pastes)
        db.session.commit()

        expire_at.day

        return render_template(
            "success_create.html", paste_id=unique_id, lifetime=lifetime
        )
        # return redirect(f"/p/{unique_id}")  # Redirect to the view page of the paste

    else:
        return render_template("create_paste.html")


@app.route("/esp-insert", methods=["GET", "POST"])
def esp_insert():
    if request.method == "POST":
        value1 = request.args.get('value1')
        value2 = request.args.get('value2')

        values = EspData(
            value1=value1,
            value2=value2,
        )
        try:
            db.session.add(values)
            db.session.commit()
            return jsonify({'message': 'values added successfully'}), 201
        except:
            db.session.rollback()
            return jsonify({'error': 'Failed to add values', 'details': str(e)}), 500


@app.route("/esp-fetch", methods=["GET"])
def esp_fetch():
    query = text('SELECT value1, value2 FROM mock_sensor_1')

    # result = db.engine.execute(query)
    result = db.session.execute(query)

    rows = result.fetchall()
    # print(rows)
    # entries = [{'value1': row['value1'], 'value2': row['value2']} for row in rows]

    data = [(row[0], row[1]) for row in rows]

    html = '<table border="1">'
    html += '<tr>' + ''.join(f'<th>Column {i+1}</th>' for i in range(2)) + '</tr>'

    # Add rows to the table
    for row in data:
        html += '<tr>' + ''.join(f'<td>{val}</td>' for val in row) + '</tr>'

    html += '</table>'

    return html, 200

    # return jsonify(str(rows)), 200


@app.route("/p/<paste_id>", methods=["GET", "POST"])
def view_paste(paste_id):
    # Retrieve the paste from the database using the paste_id
    # Return the paste content and other details
    paste_pass = (
        Paste.query.with_entities(Paste.passwd).filter(Paste.uuid == paste_id).first()
    )

    if paste_pass:
        if paste_pass[0]:
            if request.method == "POST":
                entered_password = request.form.get("passwd")

                if hash(entered_password).decode() == paste_pass[0]:
                    # Correct password entered, retrieve the full paste data
                    paste = Paste.query.filter(Paste.uuid == paste_id).first()
                    return render_template("view_paste.html", paste=paste)

                # Incorrect password entered, show an error message
                error_message = "Incorrect password, please try again!"
                return render_template(
                    "password_input.html", paste_id=paste_id, error=error_message
                )

            # Display password input form for password-protected paste
            return render_template("password_input.html")

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
