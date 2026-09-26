from decimal import Decimal
from .models import Record, ReconciliationResult

def reconcile(left: list[Record], right: list[Record], tolerance: Decimal = Decimal("0.01")):
    """Niveles: 1 referencia exacta, 2 clave contable/fecha/importe, 3 importe tolerado."""
    unused = {r.record_id: r for r in right}; out = []
    for a in sorted(left, key=lambda x: x.record_id):
        b = next((x for x in unused.values() if x.reference and x.reference == a.reference and x.currency == a.currency), None)
        level = 1
        if b is None:
            b = next((x for x in unused.values() if (x.account, x.occurred_on, x.currency, x.amount) == (a.account, a.occurred_on, a.currency, a.amount)), None); level = 2
        if b is None:
            b = next((x for x in unused.values() if x.account == a.account and x.currency == a.currency and abs(x.amount-a.amount) <= tolerance), None); level = 3
        if b:
            unused.pop(b.record_id)
            diff = a.amount - b.amount
            out.append(ReconciliationResult(level, "matched", a.record_id, b.record_id, str(diff), "coincidencia"))
        else: out.append(ReconciliationResult(0, "unmatched", a.record_id, None, str(a.amount), "sin contraparte"))
    out.extend(ReconciliationResult(0, "unmatched", "", b.record_id, str(b.amount), "sobrante") for b in unused.values())
    return out

def conciliar(left, right, tolerancia=Decimal("0.01")):
    """Nombre de API en español; conserva el orden determinista de ``reconcile``."""
    return reconcile(left, right, tolerancia)
