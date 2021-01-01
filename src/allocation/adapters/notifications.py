import abc
import smtplib
from allocation import config

class AbstractNotifications(abc.ABC):

  @abc.abstractmethod
  def send(self, destination, message):
    raise NotImplementedError

CFG = config.get_email_host_and_port()

DEFAULT_HOST = CFG['host']
DEFAULT_PORT = CFG['port']

class EmailNotifications(AbstractNotifications):

  def __init__(self, smtp_host=DEFAULT_HOST, port=DEFAULT_PORT):
    self.server = smtplib.SMTP(smtp_host, port=port)
    self.server.noop()

  def send(self, destination, message):
    msg = f'Subject: allocation service notification\n{message}'
    self.server.sendmail(
      from_addr='allocations@example.com',
      to_addrs=[destination],
      msg=msg
    )