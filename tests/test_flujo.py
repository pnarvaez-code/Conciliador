import unittest
import json
import pathlib
import tempfile
import threading
from http.server import ThreadingHTTPServer
from urllib.request import Request, urlopen
import servidor
from conciliachain.datos_prueba.generador import generar_registros
from datos_prueba.generador import empresa, banco, escribir_ejemplos
from conciliachain.apps.concilia import ejecutar
from conciliachain.utilidades.exportar import a_json
from nucleo.blockchain import Blockchain, GENESIS

class FlujoTest(unittest.TestCase):
    def test_flujo_60_58(self):
        left, right = generar_registros()
        self.assertEqual((len(left), len(right)), (60, 58))
        results = ejecutar(left, right)
        self.assertEqual(len(results), 60)
        self.assertTrue(a_json(results).startswith("["))

    def test_http_lote_extracto_verificacion_y_alteracion(self):
        with tempfile.TemporaryDirectory() as directorio:
            raiz = pathlib.Path(directorio)
            servidor.DATOS = raiz
            servidor.EVENTOS = raiz / "eventos.jsonl"
            import utilidades.emision as emision
            emision.DATOS = raiz
            emision.EVENTOS = servidor.EVENTOS
            servidor._MEM = {"empresa": empresa(), "banco": banco()}
            http = ThreadingHTTPServer(("127.0.0.1", 0), servidor.handler("empresa"))
            threading.Thread(target=http.serve_forever, daemon=True).start()
            base = f"http://127.0.0.1:{http.server_port}"
            def post(path, payload):
                req = Request(base + path, data=json.dumps(payload).encode(),
                              headers={"Content-Type": "application/json"}, method="POST")
                with urlopen(req) as response:
                    return response.status, json.loads(response.read())
            self.assertEqual(post("/cerrar_lote", {"lote": "L1"})[0], 201)
            self.assertEqual(post("/emitir_extracto?formato=csv", {"lote": "L1"})[0], 201)
            self.assertTrue(post("/verificar/L1", {})[1]["valida"])
            cadena = raiz / "empresa" / "cadena.jsonl"
            self.assertTrue(json.loads(urlopen(base + "/cadena").read())["valida"])
            self.assertEqual(urlopen(base + "/descargar_csv").status, 200)
            archivo = raiz / "empresa" / "extractos" / "L1.json"
            archivo.write_text("alterado", encoding="utf-8")
            req = Request(base + "/verificar/L1", data=b"{}", method="POST")
            with self.assertRaises(Exception):
                urlopen(req)
            http.shutdown()

    def test_ejemplos(self):
        with tempfile.TemporaryDirectory() as directorio:
            nombres = {p.name for p in escribir_ejemplos(directorio).iterdir()}
            self.assertIn("empresa_8.csv", nombres)
            self.assertIn("empresa_8.xml", nombres)
            self.assertIn("empresa_tocado_excel.csv", nombres)

    def test_blockchain_prueba_de_trabajo_y_alteracion(self):
        cadena = Blockchain(dificultad=1)
        self.assertEqual(cadena.bloques[0]["hash_anterior"], GENESIS)
        cadena.agregar([{"tipo": "lote_emitido", "lote": "L1"}], timestamp=1)
        self.assertTrue(cadena.validar())
        cadena.bloques[1]["transacciones"][0]["lote"] = "ALTERADO"
        self.assertFalse(cadena.validar())

if __name__ == "__main__":
    unittest.main()
