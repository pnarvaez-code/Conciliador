from .ports import Port
from ..deterministic import sample_records
class LedgerPort(Port):
    name = "ledger"
    def fetch(self): return sample_records()[1]
