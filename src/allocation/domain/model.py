from __future__ import annotations
from datetime import date
from dataclasses import dataclass
from typing import Optional, NewType, List, Set
from allocation.domain import events


OrderReference = NewType('OrderReference', str)
ProductReference = NewType('ProductReference', str)
Quantity = NewType("Quantity", int)
Reference = NewType("Reference", str)

class Product:
    def __init__(self, sku: str, batches: List[Batch], version_number: int = 0):
        self.sku = sku
        self.batches = batches
        self.version_number = version_number
        self.events = []

    def allocate(self, line: OrderLine, batches: List[Batch]) -> str:
        try:
            batch = next(
                b for b in sorted(batches) if b.can_allocate(line)
            )
            batch.allocate(line)
            self.version_number += 1
            return batch.reference
        except StopIteration:
            self.events.append(events.OutOfStock(line.sku))
            return ""
    
    def change_batch_quantity(self, ref: str, qty: int):
        batch = next( b for b in self.batches if b.reference == ref )
        batch._purchased_quantity = qty
        while batch.available_quantity < 0:
            line = batch.deallocate_one()
            self.events.append(
                commands.Allocate(line.orderid, line.sku, line.qty)
            )

@dataclass(unsafe_hash=True)
class OrderLine:
    orderid: OrderReference
    sku: ProductReference
    qty: int

class Batch:
    def __init__(self, ref: Reference, sku: ProductReference, qty: Quantity, eta: Optional[date]):
        self.reference = ref
        self.sku = sku
        self.eta = eta
        self._purchased_quantity = qty
        self._allocations = set()
    
    def allocate(self, line: OrderLine):
        if self.can_allocate(line):
            self._allocations.add(line)
    
    def deallocate(self, line: OrderLine):
        if line in self._allocations:
            self._allocations.remove(line)
    
    def deallocate_one(self) -> OrderLine:
        return self._allocations.pop()
    
    @property
    def allocated_quantity(self) -> int:
        return sum(line.qty for line in self._allocations)
    
    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity

    def can_allocate(self, line: OrderLine) -> bool:
        return self.sku == line.sku and self.available_quantity >= line.qty
    
    def __eq__(self, other):
        if not isinstance(other, Batch):
            return False
        return other.reference == self.reference
    
    def __hash__(self):
        return hash((self.reference))

    def __gt__(self, other):
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta
    
    def __repr__(self):
        return f'<Batch {self.reference}>'
    
