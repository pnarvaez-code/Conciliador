from .seal import digest, GENESIS
from .errors import SealError

def propagate(payload, previous=GENESIS):
    return {"payload": payload, "previous": previous, "hash": digest(payload, previous)}

def verify(item):
    previous = item.get("previous", GENESIS)
    if item.get("hash") != digest(item["payload"], previous):
        raise SealError("propagación inválida")
    return True
