"""Persistencia SQLite sin dependencias externas."""
import json
import sqlite3
from .errors import StorageError

class Database:
    def __init__(self, path="conciliachain.db"):
        self.conn = sqlite3.connect(str(path))
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys=ON")
        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS movimientos (
          id TEXT PRIMARY KEY, fuente TEXT NOT NULL, cuenta TEXT NOT NULL,
          importe TEXT NOT NULL, moneda TEXT NOT NULL, fecha TEXT NOT NULL,
          referencia TEXT NOT NULL DEFAULT '', metadata TEXT NOT NULL DEFAULT '{}'
        );
        CREATE TABLE IF NOT EXISTS records (
          source TEXT NOT NULL, record_id TEXT NOT NULL, data TEXT NOT NULL,
          PRIMARY KEY(source, record_id)
        );
        CREATE TABLE IF NOT EXISTS events (
          id TEXT PRIMARY KEY, type TEXT NOT NULL, data TEXT NOT NULL
        );
        """)
        self.conn.commit()

    def save_record(self, record):
        data = record.to_dict()
        self.conn.execute("INSERT OR REPLACE INTO records VALUES (?,?,?)",
                          (record.source, record.record_id, json.dumps(data, ensure_ascii=False)))
        self.save_movimiento(record)
        self.conn.commit()

    def save_movimiento(self, record):
        data = record.to_dict()
        self.conn.execute("""INSERT OR REPLACE INTO movimientos
          (id,fuente,cuenta,importe,moneda,fecha,referencia,metadata)
          VALUES (?,?,?,?,?,?,?,?)""",
          (record.record_id, record.source, record.account, data["amount"],
           record.currency, data["occurred_on"], record.reference,
           json.dumps(record.metadata or {}, ensure_ascii=False)))

    def guardar_movimiento(self, movimiento):
        """Guarda un Record o un diccionario con nombres en español/inglés."""
        if hasattr(movimiento, "record_id"):
            self.save_record(movimiento)
            return
        required = ("id", "fuente", "cuenta", "importe", "moneda", "fecha")
        if not all(key in movimiento for key in required):
            raise StorageError("movimiento incompleto")
        self.conn.execute("""INSERT OR REPLACE INTO movimientos
          (id,fuente,cuenta,importe,moneda,fecha,referencia,metadata)
          VALUES (?,?,?,?,?,?,?,?)""",
          (movimiento["id"], movimiento["fuente"], movimiento["cuenta"],
           str(movimiento["importe"]), movimiento["moneda"], movimiento["fecha"],
           movimiento.get("referencia", ""), json.dumps(movimiento.get("metadata", {}))))
        self.conn.commit()

    def records(self, source=None):
        query = "SELECT data FROM records"
        args = (source,) if source else ()
        if source:
            query += " WHERE source=?"
        return [json.loads(row[0]) for row in self.conn.execute(query, args)]

    def movimientos(self):
        return [dict(row) for row in self.conn.execute(
            "SELECT id,fuente,cuenta,importe,moneda,fecha,referencia,metadata "
            "FROM movimientos ORDER BY id")]

    def save_event(self, item):
        self.conn.execute("INSERT OR REPLACE INTO events VALUES (?,?,?)",
                          (item["id"], item["type"], json.dumps(item, ensure_ascii=False)))
        self.conn.commit()

    def close(self):
        self.conn.close()
