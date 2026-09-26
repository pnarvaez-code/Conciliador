"""Sellado SHA-256 y cadena JSONL de auditoría."""
import hashlib
import json
from pathlib import Path
from .errors import SealError

GENESIS = "0" * 64

def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), default=str)

def digest(value, previous=GENESIS):
    return hashlib.sha256((previous + canonical(value)).encode("utf-8")).hexdigest()

def sello(payload, anterior=GENESIS):
    return digest(payload, anterior)

def encadenar(payload, anterior=GENESIS):
    return {"previous": anterior, "payload": payload, "hash": digest(payload, anterior)}

def verificar(item, anterior=None):
    expected = item.get("previous", GENESIS) if anterior is None else anterior
    if item.get("previous", expected) != expected or item.get("hash") != digest(item["payload"], expected):
        raise SealError("sello inválido")
    return True

class JsonlChain:
    def __init__(self, path):
        self.path = Path(path)

    def append(self, payload):
        previous = GENESIS
        if self.path.exists():
            lines = [x for x in self.path.read_text(encoding="utf-8").splitlines() if x]
            if lines:
                previous = json.loads(lines[-1])["hash"]
        item = encadenar(payload, previous)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(canonical(item) + "\n")
        return item

    def verify(self):
        previous = GENESIS
        if not self.path.exists():
            return True
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError as exc:
                raise SealError("JSONL corrupto") from exc
            if item.get("previous") != previous or item.get("hash") != digest(item["payload"], previous):
                raise SealError("cadena inválida")
            previous = item["hash"]
        return True

Chain = JsonlChain
