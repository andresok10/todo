from flask import Blueprint, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField
from wtforms.validators import DataRequired
import pendulum
from babel.dates import get_month_names
import calendar
from zodiac_sign import get_zodiac_sign   # pip install zodiac-sign

app1 = Blueprint("calendario", __name__)

class FormEdad(FlaskForm):
    fecha = StringField("fecha", validators=[DataRequired()])

class FormDescuento(FlaskForm):
    monto = DecimalField("monto", validators=[DataRequired()])
    porc = DecimalField("porc", validators=[DataRequired()])

@app1.route("/", methods=["GET","POST"])
def calendario():
    f1 = FormEdad()
    f2 = FormDescuento()

    hoy = pendulum.today()

    # nombres de meses en español
    try:
        nombres = get_month_names('wide', locale='es_ES')
    except Exception:
        nombres = get_month_names('wide', locale='es')

    meses = [{
        "nombre": nombres[m],
        "mes_numero": m,
        "semanas": calendar.Calendar().monthdayscalendar(hoy.year, m)
    } for m in range(hoy.month, 13)]

    # variables por defecto
    edad = signo = cumple = fn = ""
    faltan = None
    descuento = None
    msg = ""

    # ===== FORMULARIO 1: edad + signo =====
    if f1.validate_on_submit() and f1.fecha.data:
        try:
            n = pendulum.from_format(f1.fecha.data.strip(), "DD/MM/YYYY")

            edad = hoy.diff(n).in_years()

            cumple_d = n.replace(year=hoy.year)
            if cumple_d < hoy:
                cumple_d = cumple_d.add(years=1)

            faltan = hoy.diff(cumple_d).in_days()

            # ---------- SIGNO ZODIACAL CON LIBRERÍA ----------
            signo = get_zodiac_sign(n.day, n.month)

            fn = n.format("DD/MM/YYYY")
            cumple = cumple_d.format("DD/MM/YYYY")

        except Exception:
            msg = "Datos inválidos. Formato correcto: dd/mm/aaaa"

    # ===== FORMULARIO 2: descuento =====
    if f2.validate_on_submit() and f2.monto.data and f2.porc.data:
        try:
            descuento = float(f2.monto.data) * (1 - float(f2.porc.data) / 100)
        except Exception:
            msg = "Error en cálculo de descuento"

    return render_template(
        "app.html",
        hoy=hoy,
        meses=meses,
        edad=edad,
        signo=signo,
        fn=fn,
        cumple=cumple,
        faltan=faltan,
        descuento=descuento,
        msg=msg,
        f1=f1,
        f2=f2
    )