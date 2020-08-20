from datetime import date
from dataclasses import dataclass
from typing import Optional, NewType

OrderReference = NewType('OrderReference', str)
ProductReference = NewType('ProductReference', str)
Quantity = NewType("Quantity", int)
Reference = NewType("Reference", str)

@dataclass(frozen=True)
class OrderLine:
    orderId: OrderReference
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
            self._purchased_quantity -= line.qty
    
    def deallocate(self, line: OrderLine):
        if line in self._allocations:
            self._allocations.remove(line)
    
    @property
    def allocated_quantity(self) -> int:
        return sum(line.qty for line in self._allocations)
    
    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity

    def can_allocate(self, line: OrderLine) -> bool:
        return self.sku == line.sku and self._purchased_quantity >= line.qty
    
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
    
