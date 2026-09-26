from ..reconciliation import reconcile, conciliar

def ejecutar(left, right, tolerance=None):
    return reconcile(left, right) if tolerance is None else reconcile(left, right, tolerance)

def conciliar_datos(left, right, tolerance=None):
    return ejecutar(left, right, tolerance)
