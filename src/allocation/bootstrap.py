from allocation.service_layer import unit_of_work, messagebus

def bootstrap(
  start_orm: bool = True,
  uow: unit_of_work.AbstractUnitOfWork = unit_of_work.SqlAlchemyUnitOfWork(),
  notifications: AbstractNotifications = EmailNotifications(),
  publish: Callable = redis_eventpublisher.publish,
) -> messagesbus.MessageBus:
  
  if start_orm:
    orm.start_mappers()
  
  dependencies = {'uow': uow, 'notifications': notifications, 'publish': publish}
  injected_event_handlers = {
    event_type: [
      inject_dependencies(handler, dependencies)
      for handler in event_handlers
    ]
    for event_type, event_handlers in handlers.EVENT_HANDLERS.items()
  }
  injected_command_handlers = {
    event_type: [
      inject_dependencies(handler, dependencies)
      for handler in command_handlers
    ]
    for command_type, command_handlers in handlers.COMMAND_HANDLERS.items()
  }

  return messagebus.MessageBus(
    uow=uow,
    event_handlers=injected_event_handlers,
    command_handlers=injected_command_handlers,
  )

def inject_dependencies(handler, dependencies):
  params = inspect.signature(handler).parameters
  deps = {
    name: dependency
    for name, dependency in dependencies.items()
    if name in params
  }

  return lambda message: handler(message, **deps)
