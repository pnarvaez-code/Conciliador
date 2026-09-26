"""Servidor HTTP local basado únicamente en la biblioteca estándar."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from .deterministic import sample_records
from .reconciliation import reconcile

def handler_factory():
    class Handler(BaseHTTPRequestHandler):
        def _send(self, status, body):
            raw = json.dumps(body, ensure_ascii=False, default=str).encode()
            self.send_response(status); self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(raw))); self.end_headers(); self.wfile.write(raw)
        def do_GET(self):
            if self.path in ("/health", "/api/health"):
                return self._send(200, {"status": "ok", "service": "conciliachain"})
            if self.path in ("/api/reconcile", "/reconcile"):
                a, b = sample_records(); return self._send(200, {"results": [x.to_dict() for x in reconcile(a,b)]})
            return self._send(404, {"error": "ruta no encontrada"})
        def do_POST(self):
            if self.path != "/api/reconcile": return self._send(404, {"error": "ruta no encontrada"})
            try:
                body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", "0"))))
                # Entrada HTTP sencilla: listas de records en forma JSON.
                from .models import Record
                from datetime import date
                from decimal import Decimal
                def make(x):
                    return Record(x.get("source", x.get("fuente", "unknown")),
                                  x.get("record_id", x.get("id")),
                                  x.get("account", x.get("cuenta")),
                                  Decimal(str(x.get("amount", x.get("importe")))),
                                  x.get("currency", x.get("moneda")),
                                  x.get("occurred_on", x.get("fecha")),
                                  x.get("reference", x.get("referencia", "")),
                                  x.get("metadata"))
                return self._send(200, {"results": [x.to_dict() for x in reconcile([make(x) for x in body["left"]], [make(x) for x in body["right"]])]})
            except (ValueError, KeyError, json.JSONDecodeError) as e: return self._send(400, {"error": str(e)})
        def log_message(self, *_): pass
    return Handler

def serve(host="127.0.0.1", port=8080):
    server = ThreadingHTTPServer((host, port), handler_factory())
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()
