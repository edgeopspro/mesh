from random import randint
from time import sleep

from lib.mesh.security import encode, decode
from lib.mesh.task import BackgroundTask
from lib.mesh.transporters.tcp import connect, send, receive, BasicTCP

class TCP(BasicTCP):
  def __init__(self, ctx, config):
    super().__init__()
    min, max = config['ports']
    self.ctx = ctx
    self.host = ctx.setup['srv'].split(':')[0] if 'srv' in ctx.setup else None
    self.port = randint(min, max - 1)


  def live(self, stream, interval, listener, enc='utf-8', retries=2):
    def handler(host, port, listener, enc, retries):
      msg = listener()
      send(host, [ 0, port ], msg, enc, retries)
      
    use = {
      'host': self.host,
      'port': stream,
      'listener': listener,
      'enc': enc,
      'retries': retries
    }
    return BackgroundTask(handler, use, interval)


  def rns(self, secret, enc='utf-8', retries=10, buffer=1024, handlers={}):
    def handler(ctx, host, source, enc, retries, handlers):
      def invoke(handler, data):
        if callable(handler):
          return handler(data)
        return None

      pre, proc, post = handlers
      heads, payload = receive(source, retries, buffer)
      payload = decode(payload, secret)
      size, target, encoding = heads
      state = invoke(pre, payload)
      result = None
      for mid in ctx.mids:
        state = mid(ctx, state)
      state = invoke(proc, state)
      if state:
        msg = invoke(post, state)
        send(host, [ 0, target ], encode(msg, secret), enc, retries)

    use = {
      'ctx': self.ctx,
      'host': self.host,
      'source': self.port,
      'enc': enc,
      'retries': retries,
      'handlers': handlers
    }
    return BackgroundTask(handler, use)
