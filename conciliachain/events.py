import json
from datetime import datetime, timezone
from .errors import ValidationError

def event(event_type: str, payload: dict, event_id: str | None = None):
    if not event_type: raise ValidationError("event_type requerido")
    return {"id": event_id or f"{event_type}:{payload.get('id','event')}", "type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(), "payload": payload}

def deterministic_event(event_type, payload, event_id, timestamp="2026-01-01T00:00:00+00:00"):
    """Evento reproducible para fixtures (a diferencia de :func:`event`)."""
    if not event_type or not event_id:
        raise ValidationError("tipo e id requeridos")
    return {"id": event_id, "type": event_type, "timestamp": timestamp, "payload": payload}

class EventBus:
    def __init__(self): self._handlers = {}
    def subscribe(self, event_type, handler): self._handlers.setdefault(event_type, []).append(handler)
    def publish(self, item):
        for fn in self._handlers.get(item["type"], []) + self._handlers.get("*", []): fn(item)

class JsonlEventLog:
    def __init__(self, path):
        from .seal import JsonlChain
        self.chain = JsonlChain(path)

    def append(self, event_item):
        return self.chain.append(event_item)

    def verify(self):
        return self.chain.verify()
