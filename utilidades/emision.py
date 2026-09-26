import json
from pathlib import Path
from config import DATOS, EVENTOS
from nucleo.eventos import registrar_evento
from nucleo.sello import crear_bloque, GENESIS, propagar

def emitir_extracto(actor, movimientos, lote, formato="csv"):
    from .exportar import a_csv, a_xml, a_json
    directorio = DATOS / actor / "extractos"
    directorio.mkdir(parents=True, exist_ok=True)
    ext = formato.lower()
    if ext not in ("csv", "xml", "json"): raise ValueError("formato debe ser csv, xml o json")
    contenido = {"csv": a_csv, "xml": a_xml, "json": a_json}[ext](movimientos)
    ruta = directorio / f"{lote}.{ext}"
    ruta.write_text(contenido, encoding="utf-8")
    registrar_evento(EVENTOS, "lote_emitido", {"actor": actor, "lote": lote, "archivo": ruta.name})
    return ruta

def sellar_lote(actor, movimientos, lote):
    ruta = DATOS / actor / "extractos" / f"{lote}.json"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(movimientos, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    cadena = DATOS / actor / "cadena.jsonl"
    anterior = GENESIS
    if cadena.exists():
        from nucleo.sello import leer_cadena
        anterior = leer_cadena(cadena)[-1].get("hash_bloque", GENESIS)
    bloque = crear_bloque(0, actor, lote, ruta, movimientos, anterior)
    with cadena.open("a", encoding="utf-8") as f:
        f.write(json.dumps(bloque, ensure_ascii=False, sort_keys=True) + "\n")
    registrar_evento(EVENTOS, "lote_emitido", {"actor": actor, "lote": lote})
    return bloque
