from json import loads
from re import match

from lib.mesh.ctx import BasicContext
from lib.mesh.fs import parse
from srv.mesh.core.transporters.tcp import TCP

class Context(BasicContext):
  def __init__(self, config, router):
    super().__init__(config)
    self.cache = {}
    self.router = parse(router, loads) if router else None
    self.reg('tcp_socks', lambda config: TCP(config['ports']))

  def route(self, entry, kind):
    if kind in self.router:
      router = self.router[kind]
      if entry in router:
        return [ router[entry], entry ]
      if not kind in self.cache:
        self.cache[kind] = {}
        for key, handler in router.items():
          if isinstance(handler, dict) and 'use'in handler:
            self.cache[kind][key] = [ handler['use'], handler['origin'] ]
      for key, handler in self.cache[kind].items():
        if match(key, entry):
          return handler
    return [ None, None ]