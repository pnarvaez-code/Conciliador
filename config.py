import os
from pathlib import Path

PUERTOS = {"empresa": 5001, "banco": 5002, "concilia": 5000}
PUERTO_VISOR = 5003
MODO = os.getenv("CC_MODO", "separado")
PUERTO = int(os.getenv("PORT", "8080"))
DATOS = Path(os.getenv("CC_DATOS", "datos"))
EVENTOS = DATOS / "eventos.jsonl"
COLORES = {"empresa": "#b0551b", "banco": "#1f5e8e", "concilia": "#0e7668"}

def guarani(valor):
    return f"{int(valor):,}".replace(",", ".")
