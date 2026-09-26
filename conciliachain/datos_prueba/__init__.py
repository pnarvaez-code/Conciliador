"""Datos de prueba reproducibles para demos y pruebas de integración."""
from datetime import date, timedelta
from decimal import Decimal
from ..models import Record

def generar_55_cruces():
    left, right = [], []
    for index in range(55):
        day = date(2026, 1, 1) + timedelta(days=index % 28)
        amount = Decimal("100.00") + Decimal(index)
        reference = f"REF-{index:03d}" if index < 20 else ""
        right_amount = amount if index < 40 else amount + Decimal("0.01")
        left.append(Record("bank", f"B-{index:03d}", "1000", amount, "EUR", day, reference))
        right.append(Record("ledger", f"L-{index:03d}", "1000", right_amount, "EUR", day, reference))
    return left, right

sample_55 = generar_55_cruces
