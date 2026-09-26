from dataclasses import dataclass, asdict
from datetime import date
from decimal import Decimal
from typing import Any

def _json(v: Any):
    if isinstance(v, Decimal): return str(v)
    if isinstance(v, (date,)): return v.isoformat()
    return v

@dataclass(frozen=True)
class Record:
    source: str
    record_id: str
    account: str
    amount: Decimal
    currency: str
    occurred_on: date
    reference: str = ""
    metadata: dict[str, Any] | None = None
    def __post_init__(self):
        if not isinstance(self.amount, Decimal):
            object.__setattr__(self, "amount", Decimal(str(self.amount)))
        if isinstance(self.occurred_on, str):
            object.__setattr__(self, "occurred_on", date.fromisoformat(self.occurred_on))
        if not all(isinstance(x, str) and x.strip() for x in (self.source, self.record_id, self.account, self.currency)):
            raise ValueError("source, record_id, account y currency son obligatorios")
        if self.amount.is_nan() or self.amount.is_infinite(): raise ValueError("importe inválido")
    def to_dict(self): return {k: _json(v) for k, v in asdict(self).items()}

@dataclass(frozen=True)
class ReconciliationResult:
    level: int
    status: str
    left_id: str
    right_id: str | None
    difference: str
    reason: str
    def to_dict(self): return asdict(self)
