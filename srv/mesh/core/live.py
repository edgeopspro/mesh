from json import dumps

from lib.mesh.task import BackgroundTask
from lib.mesh.parsers.stream import mid_json_out, sign_json_payload, read_json_stream
from lib.mesh.parsers.tcp_http import read_http_out
from lib.mesh.transporters import tcp
from srv.mesh.core.ops import run

encoding = 'utf-8'
subs = []

class Streamer():
  def __init__(self, ctx, port):
    self.ctx = ctx
    self.port = port
    self.task = None

  def send(self, host=None, port=None, payload=None):
    tcp.send(
      host if host else 'localhost',
      [ 0, port if port else self.port ],
      payload if payload else b'',
      enc='ascii',
      retries=2
    )

  def start(self, router, retries=2, buffer=1024):
    def handler(ctx, mids, port, retries, buffer):
      def register(ip, port, msg):
        heads, payload, info = read_http_out(msg)
        uuid, opid, ts = sign_json_payload(payload)
        if uuid:
          if not uuid in reg or len(payload) < len(reg[uuid][1]):
            reg[uuid] = [ msg, payload ]

      def stream():
        for use in reg.values():
          msg, payload = use
          pub(payload)
          run(outputs, ctx.stream.send, msg)
          
      reg = {}
      inputs, outputs = mids
      if inputs and outputs:
        heads, payload = tcp.receive(port, retries, buffer)
        run(inputs, register, payload, mid_json_out)
        stream()

    try:
      mids = router['use']
      mids = [
        mids['in'] if 'in' in mids else None,
        mids['out'] if 'out' in mids else None
      ]
      use = {
        'ctx': self.ctx,
        'mids': mids,
        'port': self.port,
        'retries': retries,
        'buffer': buffer
      }
      self.task = BackgroundTask(handler, use)
      self.task.run(wait=False)
      return self
    except Exception as error:
      return None
  
  def stop(self):
    try:
      self.send()
    except Exception:
      pass
    finally:
      self.task.stop()

def pub(payload):
  if payload and len(subs) > 0:
    if isinstance(payload, bytearray) or isinstance(payload, bytes):
      data = payload.decode(encoding)
    try:
      data = dumps(payload)
    except Exception:
      data = str(data)
    data = f'data: {data}\n\n'.encode(encoding)
    rem = []
    for sub in subs:
      if not sub(data):
        rem.append(sub)
    for sub in rem:
      subs.remove(sub)

def sub_http(req):
  def stream(payload):
    try:
      req.wfile.write(payload)
      return True
    except Exception:
      return False

  if req.wfile and callable(req.wfile.write):
    subs.append(stream)