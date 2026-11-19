import os
import random
from flask import Flask, redirect, render_template, request, session, url_for

app = Flask(__name__)
# In sviluppo va bene una chiave fissa; in produzione usa una variabile d'ambiente sicura
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "chiave-sviluppo-testa-croce")

MAX_TURNI = 5
ETICHETTE = {0: "Testa", 1: "Croce"}


def nuova_partita():
    session["turno"] = 1
    session["punti_utente"] = 0
    session["punti_pc"] = 0
    session["cronologia"] = []
    session["finita"] = False


@app.route("/", methods=["GET", "POST"])
def index():
    if "turno" not in session:
        nuova_partita()

    if request.method == "POST":
        azione = request.form.get("azione", "")

        if azione == "reset":
            nuova_partita()
            return redirect(url_for("index"))

        if not session.get("finita", False) and azione in ("0", "1"):
            scelta = int(azione)
            esito = random.randint(0, 1)
            turno_corrente = session["turno"]

            if scelta == esito:
                session["punti_utente"] += 1
                esito_turno = "utente"
                messaggio = "Hai indovinato! +1 punto per te."
            else:
                session["punti_pc"] += 1
                esito_turno = "pc"
                messaggio = "Ha indovinato il PC! +1 punto per il PC."

            cronologia = session.get("cronologia", [])
            cronologia.append({
                "turno": turno_corrente,
                "scelta": f"{scelta} ({ETICHETTE[scelta]})",
                "esito": f"{esito} ({ETICHETTE[esito]})",
                "esito_turno": esito_turno,
                "messaggio": messaggio,
            })
            session["cronologia"] = cronologia

            if turno_corrente >= MAX_TURNI:
                session["finita"] = True
            else:
                session["turno"] = turno_corrente + 1

        return redirect(url_for("index"))

    return render_template(
        "testa_croce.html",
        turno=session["turno"],
        max_turni=MAX_TURNI,
        punti_utente=session["punti_utente"],
        punti_pc=session["punti_pc"],
        cronologia=session["cronologia"],
        finita=session["finita"],
    )


if __name__ == "__main__":
    app.run(debug=True)