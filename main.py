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
import plotly.express as px
from plotly.offline import plot
import plotly.graph_objects as go
from datetime import date, timedelta

app = Flask("__name__")
app.secret_key = "somesecretkey"


class User:
    def __init__(self, id, username, password, targetWeight):
        self.id = id
        self.username = username
        self.password = password
        self.targetWeight = targetWeight

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
        users.append(User(id=item["id"], username=item["username"], password=item["password"],
                          targetWeight=item["targetWeight"]))
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
            targetWeight = request.form["targetWeight"]
            # if [x for x in users["Users"] if x["username"] == newUsername][0]:
            #    return redirect(url_for("login"))
            users["Users"].append(
                {"id": userId, "username": newUsername, "password": newPassword, "targetWeight": targetWeight})
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


def selectAllWeigths(conn):  # gibt uns Gewichte sortiert nach Datum zurück
    cur = conn.cursor()
    cur.execute("SELECT time, weight FROM weights")
    rows = cur.fetchall()
    results = []
    for row in rows:
        results.append(row)
    return list(zip(*sorted(results,
                            key=lambda x: x[1])))  # nimmt tuples auseinander und schreibt die elemente in je eine Liste


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


@app.route("/filterData", methods=["GET", "POST"])
def filterData():
    filter = request.form["zeitspanne"][0]
    conn = createConection("data/gewichtuser.db")
    weights = selectAllWeigths(conn)
    switcher = {
        "H": date.today(),
        "7": date.today() - timedelta(days=7),
        "4": date.today() - timedelta(days=30),
        "6": date.today() - timedelta(days=182),
        "1": date.today() - timedelta(days=365)
    }
    filteredWeights = []
    for x in range(0, len(weights[1])):
        item = weights[1][x]
        if datetime.strptime(item, '%y-%m-%d') >= switcher[filter]:
            filteredWeights[0].append(weights[0][x])
            filteredWeights[1].append(item)
    div = viz(filteredWeights)
    return render_template('fortschritt.html', name=g.user.username, viz_div=div)


def viz(data):
    fig = px.line(x=data[1], y=data[0], labels={"x": "date", "y": "weight"}, markers=True, title="weight")
    fig.update_traces(textposition="bottom right")
    users = jsonToUser()
    targetWeight = [x for x in users if x.username == g.user.username][0].targetWeight
    fig.add_trace(
        go.Scatter(
            x=[data[1][0], data[1][-1]],
            # dubble linked zwei listen wenn wir bei -1 sind sind wir beim letzten Element (-1 holt uns letztes ELement)
            y=[targetWeight, targetWeight],
            mode="lines",
            line=go.scatter.Line(color="gray"),
            showlegend=False)
    )

    div = plot(fig, output_type="div")
    return div


@app.route("/fortschritt", methods=["GET", "POST"])
def fortschritt():
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
    if request.method.lower() == "post":
        date = request.form["day"] + "." + request.form["month"] + "." + request.form["year"]
        dateTime = datetime.strptime(date, '%d.%m.%Y')
        weight = (request.form["Gewicht"], dateTime)
        insertWeight(conn, weight)
    weights = selectAllWeigths(conn)
    div = viz(weights)
    return render_template('fortschritt.html', name=g.user.username, viz_div=div)


@app.route("/erfassungernaehrung")
def erfassungernaehrung():
    if request.method.lower() == "get":
        print("OKAY")
        return render_template("nahrung.html")
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


def generate_chart(names, values):  # https://plotly.com/python/pie-charts/
    df = px.data.tips()  # replace with your own data source
    fig = px.pie(df, values=values, names=names, hole=.3)
    return fig


@app.route("/erfassungwasser")  # https://plotly.com/python/pie-charts/
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


@app.route("/tagebuch")
def tagebuch():
    if request.method.lower() == "get":
        return render_template("tagebuch.html")
    if request.methode.lower() == "post":
        name = request.form["vorname"]
        return name


if __name__ == "__main__":
    app.run(debug=True, port=5000)
