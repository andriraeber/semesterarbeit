from flask import Flask
from flask import render_template
from flask import url_for
from flask import request
import random

app = Flask("__name__")

"""
class benutzer:
    def __int__(self, id, benutzername, passwort):
        self.id = id
        self.benutzername = benutzername
        self.passswort = passwort

    def __repr__(self):
        return f"<User: {self.benutzername}>"

benutzer=[]
benutzer.append(benutzer(id=1, benutzername="Andri", passwort="12345"))
benutzer.append(benutzer(id=2, benutzername="Selin", passwort="6789"))

print(benutzer[1].id)
"""

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        benutzername = request.form["benutzername"]
        passwort = request.form["passwort"]
    return render_template("login.html")


@app.route("/startseite")
def about():
    return render_template("startseite.html")


@app.route("/startseite/erfassungzielgewicht")
def erfassungzielgewicht():
    return "Was ist dein Zielgewicht?"


@app.route("/startseite/erfassunggewicht")
def erfassunggewicht():
    return "Was ist dein heutiges Gewicht?"


@app.route("/startseite/erfassunggewicht/fortschritt")
def fortschritt():
    return "Dies ist dein heutiger Fortschritt!!"


@app.route("/startseite/erfassungernaehrung")
def erfassungernaehrung():
    return "Was hast du heute gegessen?"


@app.route("/startseite/erfassungernaehrung/ernaehrung")
def ernaehrung():
    return "Das ist deine Übersicht zu deiner Ernährung"


@app.route("/startseite/erfassungernaehrung/ernaehrung/kalorien")
def kalorien():
    return "Übersicht Kalorien"


@app.route("/startseite/erfassungernaehrung/ernaehrung/naehrstoffe")
def naehrstoffe():
    return "Übersicht Nährstoffe"


@app.route("/startseite/erfassungernaehrung/ernaehrung/makros")
def makros():
    return "Übersicht Makros"


@app.route("/startseite/erfassungwasser")
def erfassungwasser():
    return "erfassung Wasser"


@app.route("/startseite/erfassungwasser/wasseruebersicht")
def wasseruebersicht():
    return "heute hast du schon xy Wasser getrunken!"


@app.route("/startseite/erfassungtraining")
def erfassungtraining():
    return "erfassung Training"


@app.route("/startseite/erfassungtraining/traininguebersicht")
def traininguebersicht():
    return "traininguebersicht"


@app.route("/startseite/erfassungtagebuch/tagebuch")
def erfassungtagebuch():
    return "Wie geht es dir heute?"


@app.route("/startseite/erfassungtagebuch/tagebuchuebersicht")
def tagebuchuebersicht():
    return "Deine Tagebucheinträge der letzten Zeit."


@app.route("/form", methods=["get", "post"])
def form():
    if request.method.lower() == "get":
        return render_template("formular.html")
    if request.methode.lower() == "post":
        name = request.form["vorname"]
        return name


if __name__ == "__main__":
    app.run(debug=True, port=5000)
    

