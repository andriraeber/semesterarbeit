from flask import Flask, render_template, url_for, request, session, redirect, g
from flask import Response
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


class User:  # Definition eines User, ein User muss die Atribute: ID, Username, Passwort und Targetweight haben.
    def __init__(self, id, username, password, targetWeight):
        self.id = id
        self.username = username
        self.password = password
        self.targetWeight = targetWeight

    def __repr__(self):  # ?
        return f"<User: {self.username}>"

    def toJSON(self):  # Speichert neuen User in Json Datei ab, beginnend mit Indent 4 aufsteigend.
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


def jsonToUser():  # ?
    usersfile = open("data/users.json")
    usersjson = json.load(usersfile)
    usersfile.close()
    users = []

    for item in usersjson["Users"]:  # Speichert neuen User in Json Datei ab für spätere Wiederverwendung
        users.append(User(id=item["id"], username=item["username"], password=item["password"],
                          targetWeight=item["targetWeight"]))
    return users


@app.before_request
def before_request():  # überprüfung des Benutzer, der sich einloggen möchte.
    if "user_id" in session:
        users = jsonToUser()
        user = [x for x in users if x.id == session["user_id"]][0]
        g.user = user


@app.route("/login", methods=["GET", "POST"])
def login():  # Login eines bestehenden Benutzers
    if request.method == "POST":
        if request.form.get("registrieren") == "registrieren":
            usersfile = open("data/users.json")
            users = json.load(usersfile)  # Ist der User in der Json Datei vorhanhden?
            usersfile.close()  # ?
            userId = users["Users"][-1]["id"] + 1  # greiffe letzten Eintrag auf ([-1]) und rechne zu jener ID +1
            newUsername = request.form["username"]
            newPassword = request.form["password"]
            targetWeight = request.form["targetWeight"]
            users["Users"].append(  # Trage neuen Benutzer in User Liste in der Json Datei ein
                {"id": userId, "username": newUsername, "password": newPassword, "targetWeight": targetWeight})
            usersfile = open("data/users.json", "w")
            json.dump(users, usersfile)
            print(users)  # ?
        else:  # ?
            users = jsonToUser()
            session.pop("user_id", None)
            username = request.form["username"]
            password = request.form["password"]

            user = [x for x in users if x.username == username][0]  # Wieso hats da eine Null?
            if user and user.password == password:
                session["user_id"] = user.id
                return redirect(url_for("profile"))

            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile", methods=["GET", "POST"])
def profile():  # Aufrufen der Profielseite falls durch Falscheingabe nicht wieder auf das Login umgeleitet wurde
    if not g.user:
        return redirect("login")

    return render_template("profile.html")


@app.route("/kalorienrechner", methods=["GET", "POST"])
def erfassungzielgewicht():
    if request.method.lower() == "get":
        return render_template("erfassungzielgewicht.html")
    if request.methode.lower() == "post":
        name = request.form["vorname"]
        return name


def selectAllWeights(conn):  # gibt uns Gewichte sortiert nach Datum zurück
    cur = conn.cursor()
    cur.execute("SELECT time, weight FROM weights")
    rows = cur.fetchall()
    results = []
    for row in rows:
        results.append(row)
    return list(zip(*sorted(results,
                            key=lambda x: x[1])))  # nimmt tuples auseinander und schreibt die elemente in je eine Liste


def createConection(dbFile):  # Was passiert da Tobi? Erzeugt eine Verlinkung mit dem dbFile
    conn = None  # https://www.sqlitetutorial.net/sqlite-python/creating-database/
    try:
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
    weights = selectAllWeights(conn)
    switcher = {
        "H": date.today(),
        "7": date.today() - timedelta(days=7),
        "4": date.today() - timedelta(days=30),
        "6": date.today() - timedelta(days=182),
        "1": date.today() - timedelta(days=365)
    }
    filteredWeights = [[], []]
    for x in range(0, len(weights[1])):
        item = weights[1][x]
        if datetime.strptime(item, '%Y-%m-%d %H:%M:%S').date() >= switcher[filter]:
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
def fortschritt():  # erstellen einer neuen Table , falls noch keine vorhanden und abspeichern des Eintrages als string
    createWeightTable = """ CREATE TABLE IF NOT EXISTS weights(
                                        id integer PRIMARY KEY,
                                        time datetime NOT NULL,
                                        weight string
                                    ); """
    conn = createConection("data/gewichtuser.db")  # Ort der Table, Speicherort
    if conn is not None:
        createTable(conn, createWeightTable)
    else:
        print("Error: couldn't create table!")
    if request.method.lower() == "post":
        date = request.form["day"] + "." + request.form["month"] + "." + request.form["year"]
        dateTime = datetime.strptime(date, '%d.%m.%Y')
        weight = (request.form["Gewicht"], dateTime)
        insertWeight(conn, weight)
    weights = selectAllWeights(conn)
    div = viz(weights)
    return render_template('fortschritt.html', name=g.user.username, viz_div=div)


@app.route("/ernaehrung")
def ernaehrung():
    if request.method.lower() == "get":
        return render_template("ernaehrung.html")


"""
    def user_info(): # Anfang Einkopierter Code
    age = int(input('What is your age: '))
    gender = input('What is your gender: ')
    weight = int(input('What is your weight: '))
    height = int(input('What is your height in inches: '))

    if gender == 'male':
        c1 = 66
        hm = 6.2 * height
        wm = 12.7 * weight
        am = 6.76 * age
    elif gender == 'female':
        c1 = 655.1
        hm = 4.35 * height
        wm = 4.7 * weight
        am = 4.7 * age

    #BMR = 665 + (9.6 X 69) + (1.8 x 178) – (4.7 x 27)
    bmr_result = c1 + hm + wm - am
    return(int(bmr_result))

def calculate_activity(bmr_result):
    activity_level = input('What is your activity level (none, light, moderate, heavy, or extreme): ')

    if activity_level == 'none':
        activity_level = 1.2 * bmr_result
    elif activity_level == 'light':
        activity_level = 1.375 * bmr_result
    elif activity_level == 'moderate':
        activity_level = 1.55 * bmr_result
    elif activity_level == 'heavy':
        activity_level = 1.725 * bmr_result
    elif activity_level == 'extreme':
        activity_level = 1.9 * bmr_result

    return(int(activity_level))

def gain_or_lose(activity_level):
    goals = input('Do you want to lose, maintain, or gain weight: ')

    if goals == 'lose':
        calories = activity_level - 500
    elif goals == 'maintain':
        calories = activity_level
    elif goals == 'gain':
        gain = int(input('Gain 1 or 2 pounds per week? Enter 1 or 2: '))
        if gain == 1:
            calories = activity_level + 500
        elif gain == 2:
            calories = activity_level + 1000

    print('in order to ', goals, 'weight, your daily caloric goals should be', int(calories), '!')


gain_or_lose(calculate_activity(user_info())) # Ende Einkopierter Code
"""

if __name__ == "__main__":  # Verlinkung zur URL /500
    app.run(debug=True, port=5000)
