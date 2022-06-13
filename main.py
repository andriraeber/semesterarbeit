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


def jsonToUser():  # erstellt Liste aus Json Datei (user)
    usersfile = open("data/users.json")
    usersjson = json.load(usersfile)
    usersfile.close()
    users = []

    for item in usersjson["Users"]:  # Speichert neuen User in Json Datei ab für spätere Wiederverwendung
        users.append(User(id=item["id"], username=item["username"], password=item["password"],
                          targetWeight=item["targetWeight"]))
    return users  # ? gibt User zurück


@app.before_request
def before_request():  # überprüfung des Benutzer, der sich einloggen möchte.
    if "user_id" in session:
        users = jsonToUser()
        user = [x for x in users if x.id == session["user_id"]][0]
        g.user = user


@app.route("/", methods=["GET", "POST"])  # Loginseite mit der wir beginnen
def login():  # Login eines bestehenden Benutzers
    if request.method == "POST":
        if request.form.get("registrieren") == "registrieren":
            usersfile = open("data/users.json")
            users = json.load(usersfile)  # Ist der User in der Json Datei vorhanden?
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
        else:  # ? Tobi ist das wenn wir den User nicht erkennen?
            users = jsonToUser()
            session.pop("user_id", None)
            username = request.form["username"]
            password = request.form["password"]

            user = [x for x in users if x.username == username][0]  # Wieso hat es da eine Null?
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


@app.route("/kalorienrechner",
           methods=["GET", "POST"])  # Name stimmt noch nicht, führ in die Irre. hier wird das Zielgewixht definiert.
def erfassungzielgewicht():
    if request.method.lower() == "get":
        return render_template("erfassungzielgewicht.html")


def selectAllWeights(conn):  # gibt uns Gewichte sortiert nach Datum zurück. Conn = Reihe
    cur = conn.cursor()
    cur.execute("SELECT time, weight FROM weights")
    rows = cur.fetchall()
    results = []
    for row in rows:
        results.append(row)
    return list(zip(*sorted(results,
                            key=lambda x: x[1])))  # nimmt tuples auseinander und schreibt die elemente in je eine Liste


def createConection(dbFile):  # Was passiert da Tobi? Erzeugt eine Verlinkung mit dem dbFile? Versteh ich nicht.
    conn = None  # https://www.sqlitetutorial.net/sqlite-python/creating-database/
    try:
        conn = sqlite3.connect(dbFile)
    except Error as e:
        print(e)
    return conn


def createTable(conn,
                sqlCommand):  # https://www.sqlitetutorial.net/sqlite-python/creating-database/,  # Was passiert da Tobi? Erzeugt eine Verlinkung mit dem dbFile? Versteh ich nicht.
    try:
        c = conn.cursor()
        c.execute(sqlCommand)
    except Error as e:
        print(e)


def insertWeight(conn, weight):  # Was passiert da Tobi? Erzeugt eine Verlinkung mit dem dbFile? Versteh ich nicht.
    sql = "INSERT INTO weights(time,weight) VALUES(?,?)"
    cur = conn.cursor()
    cur.execute(sql, weight)  # sql wie funktioniert dies genau?
    conn.commit()
    return cur.lastrowid


@app.route("/filterData", methods=["GET", "POST"])  #
def filterData():
    filter = request.form["zeitspanne"][0]  # defienren des Filters, aus dem Form Zeitspanne. Stimmt das Tobi?
    conn = createConection("data/gewichtuser.db")
    weights = selectAllWeights(conn)
    switcher = {  # Definition des Switchers(Auswahlfilter) inklusive Rechnung.
        "H": date.today(),
        "7": date.today() - timedelta(days=7),
        "4": date.today() - timedelta(days=30),
        "6": date.today() - timedelta(days=182),
        "1": date.today() - timedelta(days=365)
    }
    filteredWeights = [[], []]  # Filter in der zewi Listen in der Liste
    for x in range(0, len(weights[1])):
        item = weights[1][x]
        if datetime.strptime(item, '%Y-%m-%d %H:%M:%S').date() >= switcher[
            filter]:  # hinter Y m d muss man noch die Zeitangeben und das ganze als .date() definieren Tobi wie erkläre ich .date()
            filteredWeights[0].append(weights[0][x])
            filteredWeights[1].append(item)
    div = viz(
        filteredWeights)  # was ist ein div und viz genau Tobi? Viz = visualisierung und div konnte ich nicht herausfinden.
    return render_template('fortschritt.html', name=g.user.username, viz_div=div)


def viz(data):
    fig = px.line(x=data[1], y=data[0], labels={"x": "date", "y": "weight"}, markers=True, title="weight")
    fig.update_traces(textposition="bottom right")
    users = jsonToUser()
    targetWeight = [x for x in users if x.username == g.user.username][0].targetWeight
    fig.add_trace(  # fühgt in fig ein....
        go.Scatter(
            x=[data[1][0], data[1][-1]],
            # dubble linked zwei listen wenn wir bei -1 sind sind wir beim letzten Element (-1 holt uns letztes ELement)
            y=[targetWeight, targetWeight],
            mode="lines",
            line=go.scatter.Line(color="gray"),
            showlegend=False)
    )

    div = plot(fig, output_type="div")  # drückt fig Tabelle aus.
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


@app.route("/ernaehrung", methods=["GET", "POST"])
def ernaehrung():
    if request.method == "POST":
        calories = Calories(
            session["user_id"],
            int(request.form['age']),
            request.form['gender'],
            int(request.form['weight']),
            int(request.form['height']),
            int(request.form["activity"]),
        )
        caloriesfile = open("data/calories.json")
        caloriesjson = json.load(caloriesfile) or []
        caloriesfile.close()
        caloriesjson.append(calories.toJSON())
        caloriesfile = open("data/calories.json", "wt")
        json.dump(caloriesjson, caloriesfile)
        caloriesfile.close()
        return render_template("ernaehrung.html", **calories.toJSON())
    return render_template(
        'ernaehrung.html',
    )



class Calories:  # Definition einer Calorie eingabe, ein Calorieeingabe muss die Atribute: Age, Gender, Weight und height haben.
    def __init__(self, user_id, age, gender, weight, height, activity_level):
        self.user_id = user_id
        self.age = age
        self.gender = gender
        self.weight = weight
        self.height = height
        self.bmr = self.get_Bmr()
        self.activity_level = activity_level
        self.calculated_activity = self.calculate_activity()

    def __repr__(self):  # ?
        return f"<User: {self.age}>"

    def toJSON(self):  # Speichert neuen User in Json Datei ab, beginnend mit Indent 4 aufsteigend.
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def get_Bmr(self):
        if self.gender == 'male':
            c1 = 66
            hm = 6.2 * self.height
            wm = 12.7 * self.weight
            am = 6.76 * self.age
        elif self.gender == 'female':
            c1 = 655.1
            hm = 4.35 * self.height
            wm = 4.7 * self.weight
            am = 4.7 * self.age
        else:
            return None
        # BMR = 665 + (9.6 X 69) + (1.8 x 178) – (4.7 x 27)
        return c1 + hm + wm - am

    def calculate_activity(self):
        activity_level = self.activity_level
        bmr_result = self.bmr
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

        return (int(activity_level))

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


def jsonToCalories():  # erstellt Liste aus Json Datei (calories)
    caloriesfile = open("data/calories.json")
    caloriesjson = json.load(caloriesfile)
    caloriesfile.close()
    calories = []

    for item in caloriesjson["Calories"]:  # Speichert neuen User in Json Datei ab für spätere Wiederverwendung
        calories.append(Calories(
            usere_ide=item["user_id"],
            age=item["Age"],
            gender=item["Geschlecht"],
            weight=item["Gewicht"],
            height=item["Grösse"],
            activity_level=item["activity_level"])
        )
    return calories  # ? gibt Calories zurück



if __name__ == "__main__":  # Verlinkung zur URL /500
    app.run(debug=True, port=5000)
