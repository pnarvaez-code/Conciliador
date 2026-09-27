"""Blockchain local para ConciliaChain.

No intenta ser una red pública ni una criptomoneda: es un libro mayor
inmutable local, con prueba de trabajo configurable y validación completa de
los enlaces entre bloques. Las copias pueden compararse o propagarse por la
capa de sellado existente.
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict, dataclass
from typing import Any

GENESIS = "0" * 64


def canonico(valor: Any) -> str:
    return json.dumps(valor, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256(valor: Any) -> str:
    texto = valor if isinstance(valor, bytes) else str(valor).encode("utf-8")
    return hashlib.sha256(texto).hexdigest()


@dataclass
class Bloque:
    indice: int
    timestamp: float
    transacciones: list[dict[str, Any]]
    hash_anterior: str
    nonce: int
    dificultad: int
    hash_bloque: str

    def diccionario(self) -> dict[str, Any]:
        return asdict(self)


class Blockchain:
    """Cadena append-only con prueba de trabajo y validación determinista."""

    def __init__(self, dificultad: int = 2, bloques: list[dict[str, Any]] | None = None):
        if dificultad < 0 or dificultad > 6:
            raise ValueError("la dificultad debe estar entre 0 y 6")
        self.dificultad = dificultad
        self.bloques: list[dict[str, Any]] = []
        if bloques:
            self.bloques = [dict(b) for b in bloques]
        else:
            self.bloques.append(self._minar(0, [], GENESIS, self.dificultad, timestamp=0))

    @staticmethod
    def _contenido(indice, timestamp, transacciones, anterior, nonce, dificultad):
        return canonico({
            "indice": indice, "timestamp": timestamp,
            "transacciones": transacciones, "hash_anterior": anterior,
            "nonce": nonce, "dificultad": dificultad,
        })

    def _minar(self, indice, transacciones, anterior, dificultad, timestamp=None):
        timestamp = time.time() if timestamp is None else timestamp
        nonce = 0
        prefijo = "0" * dificultad
        while True:
            valor = sha256(self._contenido(indice, timestamp, transacciones, anterior, nonce, dificultad))
            if valor.startswith(prefijo):
                return {
                    "indice": indice, "timestamp": timestamp,
                    "transacciones": transacciones, "hash_anterior": anterior,
                    "nonce": nonce, "dificultad": dificultad, "hash_bloque": valor,
                }
            nonce += 1

    def agregar(self, transacciones: list[dict[str, Any]], timestamp=None) -> dict[str, Any]:
        if not isinstance(transacciones, list) or not transacciones:
            raise ValueError("el bloque necesita al menos una transacción")
        ultimo = self.bloques[-1]
        bloque = self._minar(len(self.bloques), transacciones, ultimo["hash_bloque"],
                             self.dificultad, timestamp)
        self.bloques.append(bloque)
        return bloque

    def validar(self) -> bool:
        if not self.bloques:
            return False
        genesis = self.bloques[0]
        esperado_genesis = self._contenido(
            genesis["indice"], genesis["timestamp"], genesis["transacciones"],
            genesis["hash_anterior"], genesis["nonce"], genesis["dificultad"])
        if genesis["indice"] != 0 or genesis["hash_anterior"] != GENESIS:
            return False
        if sha256(esperado_genesis) != genesis["hash_bloque"]:
            return False
        for anterior, actual in zip(self.bloques, self.bloques[1:]):
            if actual["indice"] != anterior["indice"] + 1:
                return False
            if actual["hash_anterior"] != anterior["hash_bloque"]:
                return False
            contenido = self._contenido(
                actual["indice"], actual["timestamp"], actual["transacciones"],
                actual["hash_anterior"], actual["nonce"], actual["dificultad"])
            if sha256(contenido) != actual["hash_bloque"]:
                return False
            if not actual["hash_bloque"].startswith("0" * actual["dificultad"]):
                return False
        return True

    def exportar(self) -> list[dict[str, Any]]:
        return [dict(b) for b in self.bloques]

    @classmethod
    def importar(cls, bloques, dificultad=2):
        cadena = cls(dificultad=dificultad, bloques=bloques)
        if not cadena.validar():
            raise ValueError("blockchain inválida")
        return cadena
