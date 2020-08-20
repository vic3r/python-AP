from model import Batch, OrderLine
from datetime import datetime, timedelta
from typing import List
import pytest

class OutOfStock(Exception):
    pass

today = datetime.now()
tomorrow = today + timedelta(days=1)
later = today + timedelta(days=10)

def test_prefers_current_stock_batches_to_shipments():
    in_stocks_batch = Batch('in-stock-batch', 'RETRO-CLOCK', 100, eta=None)
    shipment_batch = Batch('shipment-batch', 'RETRO-CLOCK', 100, eta=tomorrow)
    line = OrderLine('oref', 'RETRO-CLOCK', 10)
    allocate(line, [in_stocks_batch, shipment_batch])
    assert in_stocks_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100

def test_prefere_earlier_batches():
    earliest = Batch('speedy-batch', 'MINIMALIST-SPOON', 100, eta=today)
    medium = Batch('normal-batch', 'MINIMALIST-SPOON', 100, eta=tomorrow)
    latest = Batch('slow-batch', 'MINIMALIST-SPOON', 100, eta=later)
    line = OrderLine('order1', 'MINIMALIST-SPOON', 10)
    allocate(line, [earliest, medium, latest])
    assert earliest.available_quantity == 90
    assert medium.available_quantity == 100
    assert latest.available_quantity == 100

def test_returns_allocated_batch_ref():
    in_stocks_batch = Batch('in-stock-batch', 'HIGHBROW-POSTER', 100, eta=None)
    shipment_batch = Batch('in-stock-batch', 'HIGHBROW-POSTER', 100, eta=tomorrow)
    line = OrderLine('oref', 'HIGHBROW-POSTER', 10)
    allocation = allocate(line, [in_stocks_batch, shipment_batch])
    assert allocation == in_stocks_batch.reference

def test_raises_out_of_stock_exception_if_cannot_allocate():
    batch = Batch('batch1', 'SMALL-FORK', 10, eta=today)
    allocate(OrderLine('order1', 'SMALL-FORK', 10), [batch])

    with pytest.raises(OutOfStock, match='SMALL-FORK'):
        allocate(OrderLine('order2', 'SMALL-FORK', 1), [batch])

def allocate(line: OrderLine, batches: List[Batch]) -> str:
    try:
        batch = next(b for b in sorted(batches) if b.can_allocate(line))
        batch.allocate(line)
        return batch.reference
    except StopIteration:
        raise OutOfStock(f'Out of stock for {line.sku}')
