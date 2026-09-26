import unittest
import json
from datetime import date
from decimal import Decimal
from conciliachain.deterministic import sample_records
from conciliachain.reconciliation import reconcile
from conciliachain.seal import JsonlChain
from conciliachain.propagation import propagate, verify
from conciliachain.db import Database

class EndToEndTest(unittest.TestCase):
    def test_end_to_end(self):
        import tempfile
        left, right = sample_records()
        result = reconcile(left, right)
        self.assertEqual([x.status for x in result], ["matched", "matched", "matched"])
        self.assertEqual(result[-1].difference, "-1.00")
        with tempfile.TemporaryDirectory() as directory:
            chain = JsonlChain(__import__("pathlib").Path(directory) / "events.jsonl")
            item = chain.append({"results": [x.to_dict() for x in result]})
            self.assertTrue(chain.verify()); self.assertTrue(verify(propagate(item["payload"])))
            db = Database(__import__("pathlib").Path(directory) / "data.sqlite")
            for record in left: db.save_record(record)
            self.assertEqual(len(db.records("bank")), 3)
            db.close()
