"""
from flask import Flask
from flask import render_template
from flask import url_for
from flask import request
import random

app = Flask("__name__")


@app.route("/")
def hello():
    names = ["Fabian", "Andri", "Selin", "Maurin", "Jorgi"]
    name_choice = random.choice(names)
    about_link = url_for("about")
    return render_template("index.html", name=name_choice, link=about_link)


@app.route("/about")
def about():
    return "About Test"


@app.route("/form", methods=["get", "post"])
def form():
    if request.method.lower() == "get":
        return render_template("formular.html")
    if request.methode.lower() == "post":
        name = request.form["vorname"]
        return name


if __name__ == "__main__":
    app.run(debug=True, port=5000)
"""
