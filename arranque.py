import os
import subprocess
import sys
from pathlib import Path
from config import DATOS
from datos_prueba.generador import empresa, banco
from modelo import conectar, sembrar
from nucleo.eventos import registrar_evento
from utilidades.emision import sellar_lote, emitir_extracto

def main():
    DATOS.mkdir(parents=True, exist_ok=True)
    for actor, filas in (("empresa", empresa()), ("banco", banco())):
        con = conectar(actor); con.execute("DELETE FROM movimientos"); sembrar(con, filas); con.close()
        lote = "LOTE-20260901"
        for fila in filas: fila["lote"] = lote
        sellar_lote(actor, filas, lote)
        emitir_extracto(actor, filas, lote, "csv")
    registrar_evento("datos/eventos.jsonl", "reinicio", {"modo": os.getenv("CC_MODO", "separado")})
    procesos = []
    if os.getenv("CC_MODO", "separado").lower() == "unificado":
        scripts = [("unificado.py", 8080)]
    else:
        scripts = [("empresa.py", 5001), ("banco.py", 5002), ("concilia.py", 5000), ("visor.py", 5003)]
    try:
        for script, _ in scripts:
            procesos.append(subprocess.Popen([sys.executable, str(Path(__file__).parent/"apps"/script)]))
        print("ConciliaChain: http://127.0.0.1:" + ("8080" if len(scripts) == 1 else "5000") + " (Ctrl+C para detener)")
        for p in procesos: p.wait()
    except KeyboardInterrupt:
        for p in procesos: p.terminate()

if __name__ == "__main__":
    main()
