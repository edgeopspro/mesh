from json import loads

from lib.mesh.fs import parse
from lib.mesh.utils import log, uid

class BasicContext():
  def __init__(self, conf):
    self.config = parse(conf, loads)
    self.services = {}
    self.id = uid()

  def conf(self, path):
    if not isinstance(path, list):
      path = [ path ]
    next = self.config
    for section in path:
      if section in next:
        next = next[section]
      else:
        return None
    return next

  def log(self, something):
    log(self.id, something)

  def reg(self, service, initiator):
    if not service in self.services:
      setup = self.config['services'] if 'services' in self.config else None
      if setup:
        config = setup[service] if service in setup else {}
        self.services[service] = initiator(config)
        return self.services[service]
      return None
    return self.services[service]

  def use(self, service, handler):
    if service in self.services:
      handler(self.services[service])