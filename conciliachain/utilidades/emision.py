from ..events import event, deterministic_event
from ..seal import encadenar, sello

def emitir(tipo, payload, event_id=None):
    return event(tipo, payload, event_id)

def emitir_determinista(tipo, payload, event_id):
    return deterministic_event(tipo, payload, event_id)

__all__ = ["emitir", "emitir_determinista", "encadenar", "sello"]
