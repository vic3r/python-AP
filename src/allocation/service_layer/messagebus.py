from __future__ import annotations
from tenacity import Retrying, RetryError, stop_after_attempt, wait_exponential
import logging
from typing import List, Dict, Callable, Type, Union, TYPE_CHECKING
from allocation.domain import events, commands
from . import handlers

if TYPE_CHECKING:
    from . import unit_of_work

logger = logging.getLogger(__name__)

Message = Union[commands.Command, events.Event]

class MessageBus:
  def __init__(
    self,
    uow: unit_of_work.AbstractUnitOfWork,
    event_handlers: Dict[Type[events.Event], List[Callable]],
    command_handlers: Dict[Type[commands.Command], List[Callable]],
  ):
    self.uow = uow
    self.event_handlers = event_handlers
    self.command_handlers = command_handlers

  def handle(self, message: Message):
    self.queue = [message]
    while self.queue:
      message = self.queue.pop(0)
      if isinstance(message, events.Event):
        self.handle_event(message)
      elif isinstance(message, commands.Command):
        self.handle_command(message)
        results.append(cmd_result)
      else:
        raise Exception(f'{message} was not an Event or Command')
    return results

  def handle_event(self, event: events.Event):
    for handler in self.event_handlers[type(event)]:
      try:
        for attempt in Retrying(
          stop=stop_after_attempt(3),
          wait=wait_exponential()
        ):
          with attempt:
            logger.debug('handling event %s with handler %s', event, handler)
            handler(event)
            self.queue.extend(self.uow.collect_new_events())
      except RetryError as retry_failure:
        logger.error(
          'Failed to handle event %s times, giving up!',
          retry_failure.last_attempt.attempt_number
        )
        continue

  def handle_command(self, command: commands.Command):
    logger.debug('handling command %s', command)
    try:
      handler = self.command_handlers[type(command)]
      result = handler(command)
      self.queue.extend(self.uow.collect_new_events())
      return result
    except Exception:
      logger.exception('Exception handling command %s', command)
      raise

EVENT_HANDLERS = {
  events.Allocated: [
    handlers.publish_allocate_event,
    handlers.add_allocation_to_read_model
  ],
  events.Deallocated: [
    handlers.remove_allocation_from_model,
    handlers.reallocate
  ],
  events.OutOfStock: [handlers.send_out_of_stock_notification],
}

COMMAND_HANDLERS = {
  commands.Allocate: handlers.allocate,
  commands.CreateBatch: handlers.add_batch,
  commands.ChangeBatchQuantity: handlers.change_batch_quantity,
}
