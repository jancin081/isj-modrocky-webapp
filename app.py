import hashlib
import sqlite3
import os
from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)


def db():
    conn = sqlite3.connect("treneri.db")
    return conn


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/treneri-kurzy')
def treneri_kurzy():
    conn = db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM VSETCI_TRENERI_A_ICH_KURZY")
    kurzy1 = cursor.fetchall()
    conn.close()
    return render_template("kurzy-treneri.html", kurzy1=kurzy1)


@app.route('/kurzy')
def kurzy():
    conn = db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Kurzy")
    kurzy2 = cursor.fetchall()
    conn.close()
    return render_template("kurzy.html", kurzy2=kurzy2)


@app.route("/miesta")
def miesta():
    conn = db()
    cursor = conn.cursor()
    cursor.execute("SELECT Nazov_miesta FROM Miesta")
    miesta1 = cursor.fetchall()
    conn.close()
    return render_template("miesta.html", miesta1=miesta1)


@app.route("/maximalna-kapacita-p")
def kapacita_p():
    conn = db()
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

    conn = db()
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

    conn = db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Kurzy (ID_kurzu, Nazov_kurzu, Typ_sportu, Max_pocet_ucastnikov, ID_trenera) VALUES (?, ?, ?, ?, ?)",
        (id_kurz, nazov, typ_sportu, max_ucastnici, id_trener))
    conn.commit()
    conn.close()

    return render_template("success_kurz.html")


if __name__ == '__main__':
    app.run(debug=True)
