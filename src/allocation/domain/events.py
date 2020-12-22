from dataclasses import dataclass
from typing import Optional
from datetime import date
class Event:
  pass

@dataclass
class OutOfStock(Event):
  sku: str

@dataclass
class BatchCreated(Event):
  ref: str
  sku: str
  qty: int
  eta: Optional[date]

@dataclass
class AllocationRequired(Event):
  orderid: str
  sku: str
  qty: int

