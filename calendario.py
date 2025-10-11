from flask import Blueprint, render_template, request
import calendar
from datetime import datetime

app1 = Blueprint("calendario", __name__)

signos = [
    ("Capricornio", (12, 22), (1, 19)),
    ("Acuario", (1, 20), (2, 18)),
    ("Piscis", (2, 19), (3, 20)),
    ("Aries", (3, 21), (4, 19)),
    ("Tauro", (4, 20), (5, 20)),
    ("Géminis", (5, 21), (6, 20)),
    ("Cáncer", (6, 21), (7, 22)),
    ("Leo", (7, 23), (8, 22)),
    ("Virgo", (8, 23), (9, 22)),
    ("Libra", (9, 23), (10, 22)),
    ("Escorpio", (10, 23), (11, 21)),
    ("Sagitario", (11, 22), (12, 21)),
]

@app1.route("/", methods=["GET", "POST"])
@app1.route("/calen", methods=["GET", "POST"])
def calendario():
    msg = ""
    hoy = datetime.today()
    meses = [
        {
            "nombre": calendar.month_name[m],
            "mes_numero": m,
            "semanas": calendar.Calendar().monthdayscalendar(hoy.year, m),
        }
        for m in range(hoy.month, 13)
    ]
    #print(meses)

    edad = ""
    fn = ""
    signo = ""
    cumple = ""
    faltan = None
    descuento = None

    if request.method == "POST":
        try:
            fnx = datetime.strptime(request.form.get("fecha_nacimiento", ""), "%d/%m/%Y")
            edad = hoy.year - fnx.year - ((hoy.month, hoy.day) < (fnx.month, fnx.day))
            cumplex = fnx.replace(year=hoy.year)
            print(cumplex)
            ###########
            if cumplex < hoy:
                cumplex = cumplex.replace(year=hoy.year + 1)
            ###########
            faltan = (cumplex - hoy).days
            ###########
            #signo = next(s for s, (m1, d1), (m2, d2) in signos
            #    if (fnx.month == m1 and fnx.day >= d1) or (fnx.month == m2 and fnx.day <= d2)
            #)
            
            for s, (m1, d1), (m2, d2) in signos:
                if (fnx.month == m1 and fnx.day >= d1) or (fnx.month == m2 and fnx.day <= d2):
                    signo = s
                    break
            ###########
            # aquí conviertes a string formateado
            fn = fnx.strftime("%d/%m/%Y")
            cumple = cumplex.strftime("%d/%m/%Y")
            print(cumple)
        except:
            #edad = "Ingrese fecha correcta: dia/mes/año"
            msg = ""
        ###############################################################
        try:
            monto = float(request.form.get("monto", 0))
            porcentaje = float(request.form.get("porcentaje", 0))
            descuento = monto - (monto * porcentaje / 100)
        except:
            #descuento = "Error en los datos ingresados"
            msg = ""
    
    # recoger mensajes de la descarga si existen
    msg = request.args.get("msg", "")
    msg_type = request.args.get("msg_type", "")
    download_url = request.args.get("download_url", "") # download_url=download_url,

    return render_template("app.html",
        msg=msg,
        msg_type=msg_type,
        download_url=download_url,
        hoy=hoy,
        meses=meses,
        edad=edad,
        fn=fn,
        signo=signo,
        cumple=cumple,
        faltan=faltan,
        descuento=descuento,
    )