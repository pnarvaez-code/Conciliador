import os
import subprocess
import sys
from pathlib import Path
from config import DATOS
from datos_prueba.generador import empresa, banco
from modelo import conectar, sembrar

def main():
    DATOS.mkdir(parents=True, exist_ok=True)
    for actor, filas in (("empresa", empresa()), ("banco", banco())):
        con = conectar(actor); con.execute("DELETE FROM movimientos"); sembrar(con, filas); con.close()
    procesos = []
    scripts = [("empresa.py", 5001), ("banco.py", 5002), ("concilia.py", 5000), ("visor.py", 5003)]
    try:
        for script, _ in scripts:
            procesos.append(subprocess.Popen([sys.executable, str(Path(__file__).parent/"apps"/script)]))
        print("ConciliaChain: http://127.0.0.1:5000 (Ctrl+C para detener)")
        for p in procesos: p.wait()
    except KeyboardInterrupt:
        for p in procesos: p.terminate()

if __name__ == "__main__":
    main()
