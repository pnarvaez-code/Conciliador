import unittest
from conciliachain.datos_prueba.generador import generar_registros
from conciliachain.apps.concilia import ejecutar
from conciliachain.utilidades.exportar import a_json

class FlujoTest(unittest.TestCase):
    def test_flujo_60_58(self):
        left, right = generar_registros()
        self.assertEqual((len(left), len(right)), (60, 58))
        results = ejecutar(left, right)
        self.assertEqual(len(results), 60)
        self.assertTrue(a_json(results).startswith("["))

if __name__ == "__main__":
    unittest.main()
