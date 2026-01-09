import calendar
from flask import Blueprint, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField
from wtforms.validators import DataRequired

import pendulum
from babel.dates import get_month_names
from zodiac_sign import get_zodiac_sign

app1 = Blueprint("calendario", __name__)

# -------------------------
# FORMULARIOS
# -------------------------
class FormEdad(FlaskForm):
    fecha = StringField(
        "Fecha de nacimiento (DD/MM/YYYY)",
        validators=[DataRequired()]
    )


class FormDescuento(FlaskForm):
    monto = DecimalField("Monto", validators=[DataRequired()])
    porc = DecimalField("Porcentaje", validators=[DataRequired()])


# -------------------------
# RUTA PRINCIPAL
# -------------------------
@app1.route("/", methods=["GET", "POST"])
def calendario_app():

    # ===== FECHA ACTUAL (TZ FIJA) =====
    ahora = pendulum.now("America/Guayaquil")

    f1 = FormEdad()
    f2 = FormDescuento()

    # ===== MESES EN ESPAÑOL =====
    nombres = get_month_names("wide", locale="es_ES")

    meses = [
        {
            "nombre": nombres[m],
            "mes_numero": m,
            "semanas": calendar.Calendar().monthdayscalendar(ahora.year, m),
        }
        for m in range(ahora.month, 13)
    ]

    # ===== VARIABLES SIEMPRE DEFINIDAS =====
    edad_anos, edad_meses, edad_dias = None
    #edad_anos = None
    #edad_meses = None
    #edad_dias = None

    signo = ""
    fn = ""
    cumple = ""

    diff_data = None
    descuento = None
    msg = ""

    # ===== EDAD / SIGNO / CUMPLEAÑOS =====
    if f1.validate_on_submit() and f1.fecha.data:
        try:
            nacimiento = pendulum.from_format(
                f1.fecha.data.strip(),
                "DD/MM/YYYY",
                tz="America/Guayaquil"
            )

            # ---- EDAD EXACTA ----
            periodo = nacimiento.diff(ahora)

            edad_anos = periodo.years
            edad_meses = periodo.months
            edad_dias = periodo.remaining_days

            # ---- PRÓXIMO CUMPLEAÑOS (00:00) ----
            cumple_d = pendulum.datetime(
                ahora.year,
                nacimiento.month,
                nacimiento.day,
                0, 0, 0,
                tz="America/Guayaquil"
            )

            if cumple_d <= ahora:
                cumple_d = cumple_d.add(years=1)

            diff = ahora.diff(cumple_d)

            # ---- DATOS PARA JS (SEGUROS) ----
            diff_data = {
                "days": diff.in_days(),
                "hours": diff.in_hours() % 24,
                "minutes": diff.in_minutes() % 60,
                "seconds": diff.in_seconds() % 60,
            }

            signo = get_zodiac_sign(nacimiento.day, nacimiento.month)
            fn = nacimiento.format("DD/MM/YYYY")
            cumple = cumple_d.format("DD/MM/YYYY")

        except Exception:
            msg = "Fecha inválida. Formato correcto: DD/MM/YYYY"

    # ===== DESCUENTO =====
    if f2.validate_on_submit() and f2.monto.data and f2.porc.data:
        try:
            descuento = float(f2.monto.data) * (1 - float(f2.porc.data) / 100)
        except Exception:
            msg = "Error en cálculo de descuento"

    return render_template(
        "app.html",
        ahora=ahora,
        meses=meses,
        edad_anos=edad_anos,
        edad_meses=edad_meses,
        edad_dias=edad_dias,
        signo=signo,
        fn=fn,
        cumple=cumple,
        diff_data=diff_data,
        descuento=descuento,
        msg=msg,
        f1=f1,
        f2=f2,
    )