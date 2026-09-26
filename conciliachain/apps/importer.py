import csv
from datetime import date
from decimal import Decimal
from .ports import Port
from ..models import Record
class ImportPort(Port):
    name = "import"
    def __init__(self, filename): self.filename = filename
    def fetch(self):
        with open(self.filename, newline="", encoding="utf8") as f:
            return [Record(r["source"], r["record_id"], r["account"], Decimal(r["amount"]), r["currency"], date.fromisoformat(r["occurred_on"]), r.get("reference","")) for r in csv.DictReader(f)]
