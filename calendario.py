from flask import Blueprint, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField
from wtforms.validators import DataRequired

import pendulum
import calendar
from babel.dates import get_month_names
from zodiac_sign import get_zodiac_sign

app1 = Blueprint("calendario", __name__)

# -------------------------
# FORMULARIOS
# -------------------------
class FormEdad(FlaskForm):
    fecha = StringField("Fecha de nacimiento (DD/MM/YYYY)", validators=[DataRequired()])


class FormDescuento(FlaskForm):
    monto = DecimalField("Monto", validators=[DataRequired()])
    porc = DecimalField("Porcentaje", validators=[DataRequired()])


# -------------------------
# RUTA
# -------------------------
@app1.route("/", methods=["GET", "POST"])
def calendario():

    f1 = FormEdad()
    f2 = FormDescuento()

    hoy = pendulum.today()

    # Nombres de meses en español
    try:
        nombres = get_month_names("wide", locale="es_ES")
    except Exception:
        nombres = get_month_names("wide", locale="es")

    meses = [
        {
            "nombre": nombres[m],
            "mes_numero": m,
            "semanas": calendar.Calendar().monthdayscalendar(hoy.year, m),
        }
        for m in range(hoy.month, 13)
    ]

    # Variables de salida
    edad = signo = cumple = fn = ""
    faltan = None
    descuento = None
    msg = ""

    # -------------------------
    # FORMULARIO 1: EDAD
    # -------------------------
    if f1.validate_on_submit() and f1.fecha.data:
        try:
            nacimiento = pendulum.from_format(
                f1.fecha.data.strip(), "DD/MM/YYYY"
            )

            edad = hoy.diff(nacimiento).in_years()

            cumple_d = nacimiento.replace(year=hoy.year)
            if cumple_d < hoy:
                cumple_d = cumple_d.add(years=1)

            faltan = hoy.diff(cumple_d).in_days()

            signo = get_zodiac_sign(nacimiento.day, nacimiento.month)

            fn = nacimiento.format("DD/MM/YYYY")
            cumple = cumple_d.format("DD/MM/YYYY")

        except Exception:
            msg = "Fecha inválida. Usa el formato DD/MM/YYYY"

    # -------------------------
    # FORMULARIO 2: DESCUENTO
    # -------------------------
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
        f2=f2,
    )