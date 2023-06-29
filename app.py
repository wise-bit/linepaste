from flask import Flask, render_template, request, redirect
from models import db, Paste

app = Flask(__name__)
app.debug = True


@app.route("/")
def home():
    return '<h1>Welcome to My Pastebin Clone!</h1><a href="/create">Create a New Paste</a>'


@app.route("/create", methods=["GET", "POST"])
def create_paste():
    if request.method == 'POST':
        # Process form data and create a new paste
        # Save the paste to the database

        # Assuming the newly created paste has an ID assigned
        paste_id = 123  # Replace with the actual ID of the newly created paste

        return redirect(f'/p/{paste_id}')  # Redirect to the view page of the paste
    else:
        return render_template('create_paste.html')
        
        # content = request.form.get("content")
        # title = request.form.get("title")

        # paste = Paste(content=content, title=title)
        # db.session.add(paste)
        # db.session.commit()

        # return "Paste created successfully!"

    # return render_template("create_paste.html")  # Paste creation form


@app.route("/p/<paste_id>")
def view_paste(paste_id):
    # Retrieve the paste from the database using the paste_id
    # Return the paste content and other details
    return f"Paste ID: {paste_id}"


if __name__ == "__main__":
    app.run()
