
from flask import (
    Flask,
    render_template
)


app = Flask("__name__")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/profile")
def login():
    return render_template("profile.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method.lower() == "get":
        return render_template("login.html")
    if request.methode.lower() == "post":
        name = request.form["vorname"]
        return name

