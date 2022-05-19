from flask import Flask
from flask import Response
from flask import render_template
from flask import url_for
from flask import request
from flask import session
from flask import redirect
from flask import g
import json
import sqlite3
from sqlite3 import Error
from datetime import datetime
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io

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
            # if [x for x in users["Users"] if x["username"] == newUsername][0]:
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


@app.route("/erfassungzielgewicht", methods=["GET", "POST"])
def erfassungzielgewicht():
    if request.method.lower() == "get":
        return render_template("erfassungzielgewicht.html")
    if request.methode.lower() == "post":
        name = request.form["vorname"]
        return name


@app.route("/erfassunggewicht", methods=["GET", "POST"])
def erfassunggewicht():
    createWeightTable = """ CREATE TABLE IF NOT EXISTS weights(
                                        id integer PRIMARY KEY,
                                        time datetime NOT NULL,
                                        weight string
                                    ); """
    conn = createConection("data/gewichtuser.db")
    if conn is not None:
        createTable(conn, createWeightTable)
    else:
        print("Error: couldn't create table!")
    if request.method.lower() == "get":
        return render_template("erfassunggewicht.html")
    if request.method.lower() == "post":
        date = request.form["day"] + "." + request.form["month"] + "." + request.form["year"]
        dateTime = datetime.strptime(date, '%d.%m.%Y')
        weight = (request.form["Gewicht"], dateTime)
        insertWeight(conn, weight)
        weights = selectAllWeigths(conn)
        return plotPng(weights)


def plotPng(weights):  #https://www.tutorialspoint.com/how-to-show-matplotlib-in-flask
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    ys, xs = map(list, zip(*weights))
    axis.plot(xs, ys)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


def selectAllWeigths(conn):
    cur = conn.cursor()
    cur.execute("SELECT time, weight FROM weights")
    rows = cur.fetchall()
    results = []
    for row in rows:
        results.append(row)
    return sorted(results, key=lambda x: x[1])


def createConection(dbFile):
    conn = None
    try:  # https://www.sqlitetutorial.net/sqlite-python/creating-database/
        conn = sqlite3.connect(dbFile)
    except Error as e:
        print(e)
    return conn


def createTable(conn, sqlCommand):  # https://www.sqlitetutorial.net/sqlite-python/creating-database/
    try:
        c = conn.cursor()
        c.execute(sqlCommand)
    except Error as e:
        print(e)


def insertWeight(conn, weight):
    sql = "INSERT INTO weights(time,weight) VALUES(?,?)"
    cur = conn.cursor()
    cur.execute(sql, weight)
    conn.commit()
    return cur.lastrowid


@app.route("/fortschritt")
def fortschritt():
    if request.method.lower() == "get":
        return render_template("fortschritt.html")
    if request.methode.lower() == "post":
        name = request.form["vorname"]
        return name


@app.route("/erfassungernaehrung")
def erfassungernaehrung():
    if request.method.lower() == "get":
        return render_template("erfassungernaehrung.html")
    if request.methode.lower() == "post":
        name = request.form["vorname"]
        return name


@app.route("/ernaehrung")
def ernaehrung():
    if request.method.lower() == "get":
        return render_template("ernaehrung.html")
    if request.methode.lower() == "post":
        name = request.form["vorname"]
        return name


@app.route("/makros")
def makros():
    if request.method.lower() == "get":
        return render_template("makros.html")
    if request.methode.lower() == "post":
        name = request.form["vorname"]
        return name


@app.route("/naehrstoffe")
def naehrstoffe():
    if request.method.lower() == "get":
        return render_template("naehrstoffe.html")
    if request.methode.lower() == "post":
        name = request.form["vorname"]
        return name


@app.route("/kalorien")
def kalorien():
    if request.method.lower() == "get":
        return render_template("kalorien.html")
    if request.methode.lower() == "post":
        name = request.form["vorname"]
        return name


@app.route("/erfassungwasser")
def erfassungwasser():
    if request.method.lower() == "get":
        return render_template("erfassungwasser.html")
    if request.methode.lower() == "post":
        name = request.form["vorname"]
        return name


@app.route("/erfassungtraining")
def erfassungtraining():
    if request.method.lower() == "get":
        return render_template("erfassungtraining.html")
    if request.methode.lower() == "post":
        name = request.form["vorname"]
        return name


@app.route("/uebersichttraining")
def traininguebersicht():
    if request.method.lower() == "get":
        return render_template("uebersichttraining.html")
    if request.methode.lower() == "post":
        name = request.form["vorname"]
        return name


@app.route("/tagebuch")
def tagebuch():
    if request.method.lower() == "get":
        return render_template("tagebuch.html")
    if request.methode.lower() == "post":
        name = request.form["vorname"]
        return name


if __name__ == "__main__":
    app.run(debug=True, port=5000)
