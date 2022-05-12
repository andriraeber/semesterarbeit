from flask import Flask
from flask import render_template
from flask import url_for
from flask import request
from flask import session
from flask import redirect
from flask import g
import json

app = Flask("__name__")
app.secret_key = "somesecretkey"


class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __repr__(self):
        return f"<User: {self.username}>"

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
            sort_keys=True, indent=4)


def jsonToUser():
    usersfile = open("data/users.json")
    usersjson = json.load(usersfile)
    usersfile.close()
    users = []


    for item in usersjson["Users"]:
        users.append(User(id=item["id"], username=item["username"], password=item["password"]))
    return users


@app.before_request
def before_request():
    if "user_id" in session:
        users = jsonToUser()
        user = [x for x in users if x.id == session["user_id"]][0]
        g.user = user


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("registrieren") == "registrieren":
            usersfile = open("data/users.json")
            users = json.load(usersfile)
            usersfile.close()
            userId = users["Users"][-1]["id"] + 1
            newUsername = request.form["username"]
            newPassword = request.form["password"]
            #if [x for x in users["Users"] if x["username"] == newUsername][0]:
            #    return redirect(url_for("login"))
            users["Users"].append({"id": userId, "username": newUsername, "password": newPassword})
            usersfile = open("data/users.json", "w")
            json.dump(users, usersfile)
            print(users)
        else:
            users = jsonToUser()
            session.pop("user_id", None)
            username = request.form["username"]
            password = request.form["password"]

            user = [x for x in users if x.username == username][0]
            if user and user.password == password:
                session["user_id"] = user.id
                return redirect(url_for("profile"))

            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if not g.user:
        return redirect("login")

    return render_template("profile.html")


@app.route("/startseite")
def about():
    return render_template("startseite.html")


@app.route("/startseite/erfassungzielgewicht")
def erfassungzielgewicht():
    if request.method.lower() == "get":
        return render_template("erfassungzielgewicht.html")
    if request.methode.lower() == "post":
        name = request.form["vorname"]
        return name


@app.route("/profile/erfassunggewicht")
def erfassunggewicht():
    if request.method.lower() == "get":
        return render_template("erfassunggewicht.html")
    if request.methode.lower() == "post":
        name = request.form["vorname"]
        return name


@app.route("/fortschritt")
def fortschritt():
    if request.method.lower() == "get":
        return render_template("fortschritt.html")
    if request.methode.lower() == "post":
        name = request.form["vorname"]
        return name


@app.route("/startseite/erfassungernaehrung")
def erfassungernaehrung():
    if request.method.lower() == "get":
        return render_template("erfassungernaehrung.html")
    if request.methode.lower() == "post":
        name = request.form["vorname"]
        return name


@app.route("/startseite/erfassungernaehrung/ernaehrung")
def ernaehrung():
    if request.method.lower() == "get":
        return render_template("ernaehrung.html")
    if request.methode.lower() == "post":
        name = request.form["vorname"]
        return name


@app.route("/startseite/erfassungernaehrung/ernaehrung/makros")
def makros():
    if request.method.lower() == "get":
        return render_template("makros.html")
    if request.methode.lower() == "post":
        name = request.form["vorname"]
        return name


@app.route("/startseite/erfassungernaehrung/ernaehrung/naehrstoffe")
def naehrstoffe():
    if request.method.lower() == "get":
        return render_template("naehrstoffe.html")
    if request.methode.lower() == "post":
        name = request.form["vorname"]
        return name


@app.route("/startseite/erfassungernaehrung/ernaehrung/kalorien")
def kalorien():
    if request.method.lower() == "get":
        return render_template("kalorien.html")
    if request.methode.lower() == "post":
        name = request.form["vorname"]
        return name


@app.route("/startseite/erfassungwasser")
def erfassungwasser():
    if request.method.lower() == "get":
        return render_template("erfassungwasser.html")
    if request.methode.lower() == "post":
        name = request.form["vorname"]
        return name


@app.route("/startseite/erfassungtraining")
def erfassungtraining():
    if request.method.lower() == "get":
        return render_template("erfassungtraining.html")
    if request.methode.lower() == "post":
        name = request.form["vorname"]
        return name


@app.route("/startseite/erfassungtraining/uebersichttraining")
def traininguebersicht():
    if request.method.lower() == "get":
        return render_template("uebersichttraining.html")
    if request.methode.lower() == "post":
        name = request.form["vorname"]
        return name


@app.route("/startseite/tagebuch")
def erfassungtagebuch():
    if request.method.lower() == "get":
        return render_template("tagebuch.html")
    if request.methode.lower() == "post":
        name = request.form["vorname"]
        return name


if __name__ == "__main__":
    app.run(debug=True, port=5000)
