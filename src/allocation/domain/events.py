from dataclasses import dataclass

class Event:
  pass

@dataclass
class OutOfStock(Event):
  sku: str

@dataclass
class Allocated(Command):
  orderid: str
  sku: str
  qty: int
  batchref: str

@dataclass
class Deallocated(Event):
    orderid: str
    sku: str
    qty: int
