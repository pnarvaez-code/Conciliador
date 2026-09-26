import json, os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse
from config import DATOS, EVENTOS, PUERTOS, PUERTO_VISOR
from datos_prueba.generador import empresa, banco
from modelo import conectar, registrar
from nucleo.conciliar import conciliar
from nucleo.eventos import registrar_evento, leer_eventos
from nucleo.sello import leer_cadena, verificar_cadena, verificar_archivo
from utilidades.emision import emitir_extracto, sellar_lote
from utilidades.exportar import a_csv

_MEM = {"empresa": empresa(), "banco": banco()}

def _filas(actor):
    return [dict(x) for x in _MEM["empresa" if actor == "empresa" else "banco"]]

def handler(actor):
    class Handler(BaseHTTPRequestHandler):
        def _send(self, status, body, content_type="application/json; charset=utf-8"):
            raw = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode()
            self.send_response(status); self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(raw))); self.end_headers(); self.wfile.write(raw)
        def _body(self):
            n = int(self.headers.get("Content-Length", "0"))
            return json.loads(self.rfile.read(n) or b"{}")
        def do_GET(self):
            parsed = urlparse(self.path); ruta = parsed.path
            if ruta in ("/", "/health"):
                return self._send(200, {"actor": actor, "estado": "ok", "movimientos": len(_filas(actor))})
            if ruta == "/cadena":
                cadena = DATOS / actor / "cadena.jsonl"
                return self._send(200, {"valida": verificar_cadena(cadena), "bloques": leer_cadena(cadena)})
            if ruta == "/resultado" and actor in ("concilia", "unificado"):
                pares, pendientes = conciliar(_MEM["empresa"], _MEM["banco"])
                return self._send(200, {"pares": pares, "pendientes": pendientes})
            if ruta == "/descargar_csv":
                return self._send(200, a_csv(_filas(actor)).encode(), "text/csv; charset=utf-8")
            if ruta == "/eventos":
                return self._send(200, leer_eventos(EVENTOS))
            return self._send(404, {"error": "ruta no encontrada"})
        def do_POST(self):
            parsed = urlparse(self.path); ruta = parsed.path; query = parse_qs(parsed.query)
            try: body = self._body()
            except (ValueError, json.JSONDecodeError) as exc: return self._send(400, {"error": f"JSON inválido: {exc}"})
            if ruta == "/registrar":
                if not all(k in body for k in ("fecha", "monto")): return self._send(400, {"error": "fecha y monto son obligatorios"})
                body.setdefault("descripcion", "MOVIMIENTO REGISTRADO"); _MEM[actor if actor in _MEM else "empresa"].append(body)
                try:
                    con = conectar(actor)
                    registrar(con, body)
                    con.close()
                except Exception as exc: return self._send(500, {"error": str(exc)})
                registrar_evento(EVENTOS, "movimiento_registrado", {"actor": actor, "movimiento": body})
                return self._send(201, {"ok": True, "movimiento": body})
            if ruta == "/cerrar_lote":
                lote = body.get("lote", "LOTE-20260901")
                movimientos = _filas(actor)
                for x in movimientos: x["lote"] = lote
                _MEM[actor if actor in _MEM else "empresa"] = movimientos
                bloque = sellar_lote(actor, movimientos, lote)
                return self._send(201, {"ok": True, "lote": lote, "bloque": bloque})
            if ruta == "/emitir_extracto":
                formato = query.get("formato", [body.get("formato", "csv")])[0]
                lote = body.get("lote", "LOTE-20260901")
                ruta_archivo = emitir_extracto(actor, _filas(actor), lote, formato)
                return self._send(201, {"ok": True, "archivo": ruta_archivo.name, "formato": formato})
            if ruta.startswith("/verificar/"):
                lote = ruta.rsplit("/", 1)[-1]
                cadena = DATOS / actor / "cadena.jsonl"
                valida = verificar_cadena(cadena)
                archivo = DATOS / actor / "extractos" / f"{lote}.json"
                if archivo.exists() and leer_cadena(cadena):
                    bloque = next((x for x in leer_cadena(cadena) if x.get("lote_id") == lote), None)
                    valida = valida and bloque is not None and verificar_archivo(archivo, bloque["hash_archivo"])
                registrar_evento(EVENTOS, "verificacion_integridad" if valida else "alerta_brecha", {"actor": actor, "lote": lote, "valida": valida})
                return self._send(200 if valida else 409, {"ok": valida, "lote": lote, "valida": valida})
            if ruta == "/conciliar" and actor in ("concilia", "unificado"):
                pares, pendientes = conciliar(_MEM["empresa"], _MEM["banco"])
                registrar_evento(EVENTOS, "conciliacion_ejecutada", {"pares": len(pares), "pendientes": len(pendientes)})
                return self._send(200, {"pares": pares, "pendientes": pendientes})
            return self._send(404, {"error": "ruta no encontrada"})
        def log_message(self, *args): pass
    return Handler

def servir(actor, puerto=None):
    puerto = puerto or (8080 if actor == "unificado" else PUERTOS.get(actor, PUERTO_VISOR))
    ThreadingHTTPServer(("127.0.0.1", puerto), handler(actor)).serve_forever()
