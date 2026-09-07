from __future__ import annotations

import calendar
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any

import pendulum
from babel.dates import get_month_names
from flask import Blueprint, render_template
from flask_wtf import FlaskForm
from wtforms import DecimalField, StringField
from wtforms.validators import DataRequired

from zodiac_sign import get_zodiac_sign  # pip install zodiac-sign

# ============================================================
# CONFIGURACIÓN
# ============================================================

app1 = Blueprint(
    "calendario",
    __name__,
)


TIMEZONE = "America/Guayaquil"
LOCALE = "es_ES"
DATE_FORMAT = "DD/MM/YYYY"


# ============================================================
# FORMULARIOS
# ============================================================


class FormEdad(FlaskForm):

    fecha = StringField(
        "Fecha de nacimiento (DD/MM/YYYY)",
        validators=[DataRequired()],
    )


class FormDescuento(FlaskForm):

    monto = DecimalField(
        "Monto",
        validators=[DataRequired()],
    )

    porc = DecimalField(
        "Porcentaje",
        validators=[DataRequired()],
    )


# ============================================================
# DATACLASSES
# ============================================================


@dataclass(slots=True)
class EdadResultado:

    anos: int
    meses: int
    dias: int
    signo: str
    fecha_nacimiento: str
    proximo_cumpleanos: str
    cuenta_regresiva: dict[str, int]


@dataclass(slots=True)
class CalendarioMes:

    nombre: str
    mes_numero: int
    semanas: list[list[int]]


# ============================================================
# FECHA ACTUAL
# ============================================================


def obtener_ahora() -> pendulum.DateTime:

    return pendulum.now(TIMEZONE)


# ============================================================
# CALENDARIO
# ============================================================


def obtener_meses_desde(
    ahora: pendulum.DateTime,
) -> list[CalendarioMes]:

    nombres = get_month_names(
        width="wide",
        locale=LOCALE,
    )

    calendario = calendar.Calendar(
        firstweekday=calendar.MONDAY,
    )

    return [
        CalendarioMes(
            nombre=nombres[mes],
            mes_numero=mes,
            semanas=calendario.monthdayscalendar(
                ahora.year,
                mes,
            ),
        )
        for mes in range(
            ahora.month,
            13,
        )
    ]


# ============================================================
# PARSEAR FECHA DE NACIMIENTO
# ============================================================


def parsear_fecha(
    fecha: str,
) -> pendulum.DateTime:

    fecha = fecha.strip()

    if not fecha:
        raise ValueError("La fecha está vacía")

    try:

        return pendulum.from_format(
            fecha,
            DATE_FORMAT,
            tz=TIMEZONE,
        )

    except Exception as exc:

        raise ValueError("Fecha inválida. Formato correcto: DD/MM/YYYY") from exc


# ============================================================
# PRÓXIMO CUMPLEAÑOS
# ============================================================


def obtener_proximo_cumpleanos(
    nacimiento: pendulum.DateTime,
    ahora: pendulum.DateTime,
) -> pendulum.DateTime:

    try:

        cumpleanos = pendulum.datetime(
            ahora.year,
            nacimiento.month,
            nacimiento.day,
            0,
            0,
            0,
            tz=TIMEZONE,
        )

    except ValueError:

        # Caso especial para 29 de febrero
        cumpleanos = pendulum.datetime(
            ahora.year,
            2,
            28,
            0,
            0,
            0,
            tz=TIMEZONE,
        )

    if cumpleanos <= ahora:

        siguiente_anio = ahora.year + 1

        try:

            cumpleanos = pendulum.datetime(
                siguiente_anio,
                nacimiento.month,
                nacimiento.day,
                0,
                0,
                0,
                tz=TIMEZONE,
            )

        except ValueError:

            cumpleanos = pendulum.datetime(
                siguiente_anio,
                2,
                28,
                0,
                0,
                0,
                tz=TIMEZONE,
            )

    return cumpleanos


# ============================================================
# CUENTA REGRESIVA
# ============================================================


def obtener_cuenta_regresiva(
    ahora: pendulum.DateTime,
    fecha: pendulum.DateTime,
) -> dict[str, int]:

    diferencia = ahora.diff(fecha)

    return {
        "days": diferencia.in_days(),
        "hours": diferencia.in_hours() % 24,
        "minutes": diferencia.in_minutes() % 60,
        "seconds": diferencia.in_seconds() % 60,
    }


# ============================================================
# CÁLCULO DE EDAD
# ============================================================


def calcular_edad(
    nacimiento: pendulum.DateTime,
    ahora: pendulum.DateTime,
) -> EdadResultado:

    periodo = nacimiento.diff(ahora)

    cumpleanos = obtener_proximo_cumpleanos(
        nacimiento,
        ahora,
    )

    cuenta_regresiva = obtener_cuenta_regresiva(
        ahora,
        cumpleanos,
    )

    return EdadResultado(
        anos=periodo.years,
        meses=periodo.months,
        dias=periodo.remaining_days,
        signo=get_zodiac_sign(
            nacimiento.day,
            nacimiento.month,
        ),
        fecha_nacimiento=nacimiento.format(DATE_FORMAT),
        proximo_cumpleanos=cumpleanos.format(DATE_FORMAT),
        cuenta_regresiva=cuenta_regresiva,
    )


# ============================================================
# DESCUENTO
# ============================================================


def calcular_descuento(
    monto: Decimal,
    porcentaje: Decimal,
) -> Decimal:

    if monto < 0:

        raise ValueError("El monto no puede ser negativo")

    if porcentaje < 0 or porcentaje > 100:

        raise ValueError("El porcentaje debe estar entre 0 y 100")

    resultado = monto * (Decimal("1") - porcentaje / Decimal("100"))

    return resultado.quantize(Decimal("0.01"))


# ============================================================
# SERIALIZAR EDAD PARA JINJA / JS
# ============================================================


def edad_to_dict(
    resultado: EdadResultado,
) -> dict[str, Any]:

    return {
        "anos": resultado.anos,
        "meses": resultado.meses,
        "dias": resultado.dias,
        "signo": resultado.signo,
        "fecha_nacimiento": resultado.fecha_nacimiento,
        "proximo_cumpleanos": (resultado.proximo_cumpleanos),
        "cuenta_regresiva": (resultado.cuenta_regresiva),
    }


# ============================================================
# RUTA
# ============================================================


@app1.route(
    "/",
    methods=["GET", "POST"],
)
def calendario_app():

    ahora = obtener_ahora()

    f1 = FormEdad()
    f2 = FormDescuento()

    meses = obtener_meses_desde(ahora)

    edad: EdadResultado | None = None

    descuento: Decimal | None = None

    mensaje = ""

    # ========================================================
    # EDAD
    # ========================================================

    if f1.validate_on_submit() and f1.fecha.data:

        try:

            nacimiento = parsear_fecha(f1.fecha.data)

            if nacimiento > ahora:

                raise ValueError("La fecha de nacimiento " "no puede ser futura")

            edad = calcular_edad(
                nacimiento,
                ahora,
            )

        except ValueError as exc:

            mensaje = str(exc)

        except Exception:

            mensaje = "No se pudo procesar " "la fecha de nacimiento"

    # ========================================================
    # DESCUENTO
    # ========================================================

    if (
        f2.validate_on_submit()
        and f2.monto.data is not None
        and f2.porc.data is not None
    ):

        try:

            descuento = calcular_descuento(
                Decimal(str(f2.monto.data)),
                Decimal(str(f2.porc.data)),
            )

        except (
            ValueError,
            InvalidOperation,
        ) as exc:

            mensaje = str(exc)

        except Exception:

            mensaje = "Error al calcular el descuento"

    return render_template(
    "app.html",
    ahora=ahora,
    meses=meses,
    f1=f1,
    f2=f2,
    msg=mensaje,
    edad_anos=edad.anos if edad else None,
    edad_meses=edad.meses if edad else None,
    edad_dias=edad.dias if edad else None,
    signo=edad.signo if edad else None,
    fn=edad.fecha_nacimiento if edad else None,
    cumple=edad.proximo_cumpleanos if edad else None,
    diff_data=edad.cuenta_regresiva if edad else None,
    descuento=descuento,
    )