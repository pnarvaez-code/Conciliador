import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
from config import PUERTOS, PUERTO_VISOR
from datos_prueba.generador import empresa, banco
from nucleo.conciliar import conciliar

def handler(actor):
    class Handler(BaseHTTPRequestHandler):
        def _send(self, status, body, content_type="application/json; charset=utf-8"):
            raw = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode()
            self.send_response(status); self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(raw))); self.end_headers(); self.wfile.write(raw)
        def do_GET(self):
            ruta=urlparse(self.path).path
            if ruta in ("/", "/health", "/cadena"):
                return self._send(200, {"actor": actor, "estado": "ok", "movimientos": len(empresa() if actor=="empresa" else banco())})
            if actor=="concilia" and ruta=="/resultado":
                pares, pendientes=conciliar(empresa(),banco()); return self._send(200, {"pares":pares,"pendientes":pendientes})
            return self._send(404, {"error":"ruta no encontrada"})
        def do_POST(self):
            ruta=urlparse(self.path).path
            if actor=="concilia" and ruta=="/conciliar":
                pares, pendientes=conciliar(empresa(),banco()); return self._send(200, {"pares":pares,"pendientes":pendientes})
            if ruta in ("/registrar","/cerrar_lote","/verificar") or ruta.startswith("/verificar/"):
                return self._send(200, {"ok":True,"actor":actor})
            return self._send(404, {"error":"ruta no encontrada"})
        def log_message(self,*args): pass
    return Handler

def servir(actor, puerto=None):
    puerto = puerto or (PUERTOS.get(actor) if actor != "visor" else PUERTO_VISOR)
    ThreadingHTTPServer(("127.0.0.1", puerto), handler(actor)).serve_forever()
