from .ports import Port
from ..deterministic import sample_records

class EmpresaPort(Port):
    name = "empresa"
    def fetch(self):
        return sample_records()[1]

Empresa = EmpresaPort
