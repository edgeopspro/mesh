from lib.mesh.transporters.http import fetch
from lib.mesh.utils import ts

class HTTP():
  def __init__(self, ctx, config):
    self.config = config if isinstance(config, dict) else {}
    self.ctx = ctx
    self.use = {
      'host': ctx.setup['srv'] if 'srv' in ctx.setup else None,
      'method': self.config['method'] if 'method' in self.config else 'POST'
    }

  def fetch(self, input, infmt=None, outfmt=None):
    def format(obj, handler):
      if callable(handler):
        payload = obj['payload'] if 'payload' in obj else None
        if payload:
          try:
            obj['payload'] = handler(payload)
          except Exception:
            pass

    format(input, infmt)
    output = fetch({ **input, **self.use }, self.config)
    output['id'] = self.ctx.id
    self.ctx.log(output)
    format(output, outfmt)
    return output