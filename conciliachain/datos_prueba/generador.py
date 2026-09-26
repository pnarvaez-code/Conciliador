"""Generador determinista de los fixtures oficiales (60 y 58 registros)."""
from datetime import date, timedelta
from decimal import Decimal
from ..models import Record

def registros(cantidad, fuente):
    return [Record(fuente, f"{fuente[:1].upper()}-{i:03d}", "1000",
                   Decimal("10.00") + i, "EUR",
                   date(2026, 1, 1) + timedelta(days=i % 30),
                   f"REF-{i:03d}") for i in range(cantidad)]

def generar_registros():
    return registros(60, "bank"), registros(58, "ledger")

def ejemplos():
    left, right = generar_registros()
    return {"banco": left[:3], "empresa": right[:3], "left": left, "right": right}

generar = generar_registros
