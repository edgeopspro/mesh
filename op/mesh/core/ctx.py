from lib.mesh.ctx import BasicContext
from op.mesh.core.transporters.http import HTTP
from op.mesh.core.transporters.tcp import TCP

class Context(BasicContext):
  def __init__(self, cyc, mids, conf):
    super().__init__(conf)
    self.data = {}
    self.lifecycle = cyc
    self.mids = mids
    self.setup = self.config['mesh'] if 'mesh' in self.config else {}
    self.reg('http', lambda config: HTTP(self, config))
    self.reg('tcp', lambda config: TCP(self, config))
    self.stream = None


  def trigger(self, use, payload=None, handler=None):
    def invoke(handler, data):
      if callable(handler):
        return handler(self, data) if data else handler(self)
      return None

    if isinstance(use, list):
      for mid in use:
        invoke(handler, invoke(mid, payload))
      return True
    else:
      result = invoke(self.lifecycle[use], payload)
      return invoke(handler, result) if handler else result
