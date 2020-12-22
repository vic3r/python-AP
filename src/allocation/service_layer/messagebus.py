from allocation.domain import events
from allocation.domain import events
from . import handlers, unit_of_work

def handle(event: events.Event, uow: unit_of_work.AbstractUnitOfWork):
    queue = [event]
    while queue:
        event = queue.pop(0)
        for handler in HANDLERS[type(event)]:
            handler(event, uow=uow)
            queue.extend(uow.collect_new_events())

HANDLERS = {
    events.OutOfStock: [handlers.send_out_of_stock_notification],
}
