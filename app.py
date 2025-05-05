import hashlib

from flask import Flask, request, render_template
import sqlite3

app = Flask(__name__)


def db():
    conn = sqlite3.connect("treneri.db")
    return conn


@app.route('/')
def index():
    return '''
    <h1>Výber z databázy</h1>
        <a href="/treneri-kurzy"><button>Zobraz všetkých trénerov a ich kurzy</button></a>
        <a href="/kurzy"><button>Zobraz všetky kurzy</button></a>
        <a href="/miesta"><button>Zobraz všetky miesta</button></a>
        <a href="/maximalna-kapacita-p"><button>Výpis súčtu maximálnej kapacity všetkých kurzov, ktoré začínajú na písmeno P</button></a>
        <a href="/registracia"><button>Registruj trénera</button></a>
        <a href="/pridaj_kurz"><button>Pridaj kurz</button></a>
        <hr>
    '''


@app.route('/treneri-kurzy')
def treneri_kurzy():
    conn = db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM VSETCI_TRENERI_A_ICH_KURZY")
    kurzy1 = cursor.fetchall()
    conn.close()

    return render_template("kurzy.html", kurzy1=kurzy1)


@app.route('/kurzy')
def kurzy():
    conn = db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Kurzy")
    kurzy2 = cursor.fetchall()
    conn.close()
    vystup = "<h2> Zoznam vsetkych kurzzov: </h2>"
    for kurz in kurzy2:
        vystup += f"<p> {kurz} </p>"
    vystup += '<a href="/">Späť</a>'
    return vystup


@app.route("/miesta")
def miesta():
    conn = db()
    cursor = conn.cursor()
    cursor.execute("SELECT Nazov_miesta FROM Miesta")
    miesta1 = cursor.fetchall()
    conn.close()
    vystup = "<h2> Zoznam vsetkych miest: </h2>"
    for miesto in miesta1:
        vystup += f"<p> {miesto} </p>"
    vystup += '<a href="/">Späť</a>'
    return vystup


@app.route("/maximalna-kapacita-p")
def kapacita_p():
    conn = db()
    cursor = conn.cursor()
    cursor.execute("SELECT sum(Max_pocet_ucastnikov) AS Kapacita FROM Kurzy WHERE Nazov_kurzu LIKE 'P%';")
    kapacita_miesta = cursor.fetchall()
    conn.close()
    vystup = "<h2> Kapacita miest, ktore sa zacinaju na P: </h2>"
    for kapacita in kapacita_miesta:
        vystup += f"<p> {kapacita} </p>"
    vystup += '<a href="/">Späť</a>'
    return vystup


@app.route("/registracia", methods=['GET'])
def registracia_form():
    return '''
    <h2>Registrácia trénera</h2>
    <form action="/registracia" method="post">
    <label>Meno:</label><br>
    <input type="text" name="meno" required><br><br>
    <label>Priezvisko:</label><br>
    <input type="text" name="priezvisko" required><br><br>
    <label>Špecializácia:</label><br>
    <input type="text" name="specializacia" required><br><br>
    <label>Telefón:</label><br>
    <input type="text" name="telefon" required><br><br>
    <label>Heslo:</label><br>
    <input type="password" name="heslo" required><br><br>

    <button type="submit">Registrovať</button>
    </form>
    <hr>
    <a href="/">Späť</a>
    '''


@app.route("/registracia", methods=['POST'])
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

    return '''
    <h2>Tréner bol úspešne zaregistrovaný!</h2>
    <hr>
    <a href="/">Späť</a>
    '''


@app.route("/pridaj_kurz", methods=['GET'])
def pridat_kurz_form():
    return '''
     <h2>Pridaj Kurz</h2>
    <form action="/pridaj_kurz" method="post">
    <label>Názov kurzu:</label><br>
    <input type="text" name="nazov" required><br><br>
    <label>Typ Športu:</label><br>
    <input type="text" name="typ_sportu" required><br><br>
    <label>Maximálny počet účastníkov:</label><br>
    <input type="text" name="max_ucastnici" required><br><br>
    <label>ID trénera:</label><br>
    <input type="text" name="id_trenera" required><br><br>
    <label>ID nového kurzu:</label><br>
    <input type="text" name="id_kurzu" required><br><br>

    <button type="submit">Pridať kurz</button>
    </form>
    <hr>
    <a href="/">Späť</a>
    '''


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

    return '''
    <h2>Kurz bol úspešne pridaný!</h2>
    <hr>
    <a href="/">Späť</a>
    '''


if __name__ == '__main__':
    app.run(debug=True)
