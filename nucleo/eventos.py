import json, time
from pathlib import Path
def registrar_evento(ruta, tipo, datos=None):
    p=Path(ruta); p.parent.mkdir(parents=True,exist_ok=True)
    eventos=leer_eventos(p); item={"id":len(eventos)+1,"timestamp":time.time(),"tipo":tipo,"datos":datos or {}}
    with p.open("a",encoding="utf-8") as f: f.write(json.dumps(item,ensure_ascii=False)+"\n")
    return item
def leer_eventos(ruta):
    p=Path(ruta)
    if not p.exists(): return []
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]
