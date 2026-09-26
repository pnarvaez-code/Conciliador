from datetime import date
from decimal import Decimal
from .models import Record

def sample_records():
    left = [
        Record("bank", "B-001", "1000", Decimal("100.00"), "EUR", date(2026, 1, 2), "ORDER-1"),
        Record("bank", "B-002", "1000", Decimal("25.50"), "EUR", date(2026, 1, 3), "ORDER-2"),
        Record("bank", "B-003", "1000", Decimal("7.00"), "EUR", date(2026, 1, 4), "ORDER-3"),
    ]
    right = [
        Record("ledger", "L-001", "1000", Decimal("100.00"), "EUR", date(2026, 1, 2), "ORDER-1"),
        Record("ledger", "L-002", "1000", Decimal("25.50"), "EUR", date(2026, 1, 3), "ORDER-2"),
        Record("ledger", "L-003", "1000", Decimal("8.00"), "EUR", date(2026, 1, 4), "ORDER-3"),
    ]
    return left, right
