import hashlib
import sqlite3
import os
from flask import Flask, request, render_template, g, session
from flask_sqlalchemy import SQLAlchemy
from i18n import TRANSLATIONS, SUPPORTED

app = Flask(__name__, instance_relative_config=True)
app.secret_key = "tajny_kluc"
db_path = os.path.join(app.instance_path, "treneri.db")

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}".replace("\\", "/")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


def db_connect():
    conn = sqlite3.connect("instance/treneri.db")
    return conn


@app.before_request
def set_lang():
    lang = request.args.get("lang")
    if lang not in SUPPORTED:
        lang = session.get('lang', 'sk')
    session["lang"] = lang
    g.t = TRANSLATIONS[lang]

@app.context_processor
def inject_translations():
    return dict(t=g.t)


class Kurz(db.Model):
    __tablename__ = "Kurzy"
    ID_kurzu = db.Column(db.Integer, primary_key=True)
    Nazov_kurzu = db.Column(db.String, nullable=False)
    Typ_sportu = db.Column(db.String)
    Max_pocet_ucastnikov = db.Column(db.Integer)
    ID_trenera = db.Column(db.Integer)


class Miesta(db.Model):
    __tablename__ = "Miesta"
    ID_miesta = db.Column(db.Integer, primary_key=True)
    Nazov_miesta = db.Column(db.String, nullable=False)
    Adresa = db.Column(db.String)
    Kapacita = db.Column(db.Integer)


class TreneriKurzyView(db.Model):
    __tablename__ = "VSETCI_TRENERI_A_ICH_KURZY"
    ID_trenera = db.Column(db.Integer)
    Meno = db.Column(db.String)
    Priezvisko = db.Column(db.String)
    Nazov_kurzu = db.Column(db.String)

    __mapper_args__ = {
        "primary_key": [ID_trenera, Nazov_kurzu]
    }


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/treneri-kurzy')
def treneri_kurzy():
    kurzy1 = TreneriKurzyView.query.all()
    return render_template("kurzy-treneri.html", kurzy1=kurzy1)


@app.route('/kurzy')
def kurzy():
    kurzy_zobraz = Kurz.query.all()
    return render_template("kurzy.html", kurzy2=kurzy_zobraz)


@app.route("/miesta")
def miesta():
    miesta1 = Miesta.query.all()
    return render_template("miesta.html", miesta1=miesta1)


@app.route("/maximalna-kapacita-p")
def kapacita_p():
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT sum(Max_pocet_ucastnikov) AS Kapacita FROM Kurzy WHERE Nazov_kurzu LIKE 'P%';")
    kapacita_miesta = cursor.fetchall()
    conn.close()
    return render_template("maximalna-kapacita-p.html", kapacita_miesta=kapacita_miesta)


@app.route("/registracia-trenera", methods=['GET'])
def registracia_form():
    return render_template("registracia-trenera.html")


@app.route("/registracia-trenera", methods=['GET', 'POST'])
def registracia_trenera():
    meno = request.form['meno']
    priezvisko = request.form['priezvisko']
    specializacia = request.form['specializacia']
    telefon = request.form['telefon']
    heslo = request.form['heslo']
    heslo_hash = hashlib.sha256(heslo.encode()).hexdigest()

    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Treneri (Meno, Priezvisko, Specializacia, Telefon, Heslo) VALUES (?, ?, ?, ?, ?)",
                   (meno, priezvisko, specializacia, telefon, heslo_hash))
    conn.commit()
    conn.close()

    return render_template("success.html")


@app.route("/pridaj_kurz", methods=['GET'])
def pridat_kurz_form():
    return render_template("pridaj_kurz.html")


def sifrovanie(text):
    sifrovany_text = ""
    for char in text:
        if char.isalpha():
            char = char.upper()
            cislopismena = ord(char) - ord('A')
            sifrovane = (5 * int(cislopismena) + 8) % 26
            sifrovany_text += chr(sifrovane + ord('A'))
        else:
            sifrovany_text += char
    return sifrovany_text


@app.route("/pridaj_kurz", methods=['POST'])
def pridaj_kurz():
    nazov = sifrovanie(request.form['nazov'])
    typ_sportu = sifrovanie(request.form['typ_sportu'])
    max_ucastnici = request.form['max_ucastnici']
    id_trener = request.form['id_trenera']
    id_kurz = request.form['id_kurzu']

    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Kurzy (ID_kurzu, Nazov_kurzu, Typ_sportu, Max_pocet_ucastnikov, ID_trenera) VALUES (?, ?, ?, ?, ?)",
        (id_kurz, nazov, typ_sportu, max_ucastnici, id_trener))
    conn.commit()
    conn.close()

    return render_template("success_kurz.html")


if __name__ == '__main__':
    app.run(debug=True)
