from random import randint

from lib.mesh.parsers.tcp import msg
from lib.mesh.task import BackgroundTask
from lib.mesh.transporters.tcp import connect, send, receive, BasicTCP

class TCP(BasicTCP):
  def __init__(self, ctx, config):
    super().__init__()
    min, max = config['ports']
    self.ctx = ctx
    self.host = ctx.setup['srv'].split(':')[0] if 'srv' in ctx.setup else None
    self.port = randint(min, max - 1)

  def rns(self, enc='utf-8', retries=10, buffer=1024, handlers={}):
    def handler(ctx, host, source, enc, retries, handlers):
      def invoke(handler, data):
        if callable(handler):
          return handler(data)
        return None

      pre, post = handlers
      heads, payload = receive(source, retries, buffer)
      size, target, encoding = heads
      state = invoke(pre, payload)
      result = None
      for mid in ctx.mids:
        state = mid(ctx, state)
      send(host, [ 0, target ], invoke(post, state), enc, retries)

    use = {
      'ctx': self.ctx,
      'host': self.host,
      'source': self.port,
      'enc': enc,
      'retries': retries,
      'handlers': handlers
    }
    return BackgroundTask(handler, use)
