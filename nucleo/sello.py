import hashlib, json, time
from pathlib import Path
GENESIS = "0" * 64
def huella(valor):
    return hashlib.sha256(str(valor).encode("utf-8")).hexdigest()
def huella_movimiento(m):
    return huella(f"{m['fecha']}|{int(m['monto'])}|{m.get('referencia','').strip().upper()}|{m.get('descripcion','').strip()}")
def huella_archivo(ruta):
    return huella(Path(ruta).read_bytes())
def leer_cadena(ruta):
    texto = Path(ruta).read_text(encoding="utf-8") if Path(ruta).exists() else ""
    dec = json.JSONDecoder(); pos = 0; salida = []
    while pos < len(texto):
        while pos < len(texto) and texto[pos].isspace(): pos += 1
        if pos >= len(texto): break
        try: obj, pos = dec.raw_decode(texto, pos); salida.append(obj)
        except json.JSONDecodeError: break
    return salida
def _canon(x): return json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
def crear_bloque(indice, origen, lote_id, archivo, movimientos, anterior=GENESIS):
    hs = [huella_movimiento(x) for x in movimientos]
    bloque = {"indice": indice, "origen": origen, "lote_id": lote_id, "archivo": Path(archivo).name,
      "n_movimientos": len(movimientos), "hashes_movimientos": hs, "hash_raiz": huella("".join(hs)),
      "hash_archivo": huella_archivo(archivo), "hash_anterior": anterior, "timestamp": int(time.time())}
    bloque["hash_bloque"] = huella(_canon(bloque)); return bloque
def propagar(bloque, receptores):
    for ruta in receptores:
        p = Path(ruta); p.parent.mkdir(parents=True, exist_ok=True)
        previo = leer_cadena(p)
        if previo and bloque["hash_anterior"] != previo[-1].get("hash_bloque", GENESIS):
            raise ValueError("brecha de cadena")
        with p.open("a", encoding="utf-8") as f: f.write(_canon(bloque) + "\n")
def verificar_cadena(ruta):
    previo = GENESIS
    for b in leer_cadena(ruta):
        if b.get("hash_anterior") != previo: return False
        copia = dict(b); esperado = copia.pop("hash_bloque", None)
        if huella(_canon(copia)) != esperado: return False
        previo = esperado
    return True
def verificar_archivo(ruta, esperado): return huella_archivo(ruta) == esperado
def verificar_movimientos(movs, hashes): return [huella_movimiento(x) for x in movs] == list(hashes)
def comparar_copias(*rutas): return all(verificar_cadena(r) for r in rutas)
