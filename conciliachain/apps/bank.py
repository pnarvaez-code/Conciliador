from .ports import Port
from ..deterministic import sample_records
class BankPort(Port):
    name = "bank"
    def fetch(self): return sample_records()[0]
