import sqlite3
from pathlib import Path

def conectar(actor, base="datos"):
    ruta = Path(base) / actor / "movimientos.sqlite3"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(ruta)
    con.row_factory = sqlite3.Row
    con.execute("""CREATE TABLE IF NOT EXISTS movimientos
      (id INTEGER PRIMARY KEY, lote TEXT, fecha TEXT NOT NULL, monto INTEGER NOT NULL,
       referencia TEXT DEFAULT '', descripcion TEXT DEFAULT '')""")
    con.commit()
    return con

def sembrar(con, filas):
    con.executemany("INSERT OR REPLACE INTO movimientos(lote,fecha,monto,referencia,descripcion) VALUES(?,?,?,?,?)",
                    [(x.get("lote"), x["fecha"], int(x["monto"]), x.get("referencia",""), x.get("descripcion","")) for x in filas])
    con.commit()

def registrar(con, movimiento):
    sembrar(con, [movimiento])

def resumen(con):
    return {"cantidad": con.execute("SELECT COUNT(*) FROM movimientos").fetchone()[0],
            "monto": con.execute("SELECT COALESCE(SUM(monto),0) FROM movimientos").fetchone()[0]}

def listar_pendientes(con):
    return [dict(x) for x in con.execute("SELECT * FROM movimientos WHERE lote IS NULL ORDER BY id")]

def listar_por_lote(con, lote):
    return [dict(x) for x in con.execute("SELECT * FROM movimientos WHERE lote=? ORDER BY id", (lote,))]
