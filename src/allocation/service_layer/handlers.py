from __future__ import annotations
from typing import TYPE_CHECKING
from allocation.adapters import email
from allocation.domain import commands, model, events
from allocation.domain.model import OrderLine
if TYPE_CHECKING:
    from . import unit_of_work

class InvalidSku(Exception):
    pass

def add_batch(
    cmd: commands.CreateBatch,
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:
        product = uow.products.get(sku=cmd.sku)
        if product is None:
            product = model.Product(cmd.sku, batches=[])
            uow.products.add(product)
        product.batches.append(model.Batch(
            cmd.ref, cmd.sku, cmd.qty, cmd.eta
        ))
        uow.commit()


def allocate(
    cmd: commands.Allocate,
    uow: unit_of_work.AbstractUnitOfWork
) -> str:
    line = OrderLine(cmd.orderid, cmd.sku, cmd.qty)
    with uow:
        product = uow.products.get(sku=line.sku)
        if product is None:
            raise InvalidSku(f'Invalid sku {line.sku}')
        batchref = product.allocate(line)
        uow.commit()
        return batchref

def change_batch_quantity(
    cmd: commands.ChangeBatchQuantity,
    uow: unit_of_work.AbstractUnitOfWork
):
    with uow:
        product = uow.product.get_by_batchref(batchref=event.ref)
        product.change_batch_quantity(ref=cmd.ref, quantity=cmd.qty)
        uow.commit()

def send_out_of_stock_notification(event: events.OutOfStock, uow: unit_of_work.AbstractUnitOfWork):
    email.send_email(
        'stock@made.com',
        f'Out of stock for {event.sku}',
    )

def publish_allocate_event(event: events.Allocate, uow: unit_of_work.AbstractUnitOfWork):
    redis_eventpublisher.publish('line_allocated', event)

def add_allocation_to_read_model(event: events.Allocate, uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        uow.session.execute(
            'INSERT INTO allocations_view (orderid, sku, batchref)'
            'VALUES (:orderid, :sku, :batchref)',
            dict(orderid=event.orderid, sku=event.sku, batchref=event.batchref)
        )
        uow.commit()

def remove_allocation_from_model(event: events.Deallocate, uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        uow.session.execute(
            'DELETE FROM allocation_view'
            ' WHERE orderid = :orderid AND sku = :sku',
            dict(orderid=event.orderid, sku=event.sku)
        )
        uow.commit()
