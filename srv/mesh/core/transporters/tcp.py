from time import sleep

from lib.mesh.task import Task
from lib.mesh.transporters.tcp import send, receive, BasicTCP
from srv.mesh.core.live import Streamer

class TCP(BasicTCP):
  def __init__(self, ports):
    super().__init__()
    min, max = ports
    self.socks = {}
    for port in range(min, max + 1):
      self.socks[port] = False
    self.stream = Streamer(self, self.use())


  def snr(self, ip, port, msg, enc='utf-8', retries=10, buffer=1024):
    def handler(ip, ports, msg, output, enc, retries):
      send(ip, ports, msg, enc, retries)
      heads, payload = receive(ports[0], retries, buffer)
      output.extend(payload)

    use = self.use()
    output = bytearray()
    while not use:
      sleep(.1)
    try:
      Task(handler, (ip, [ use, port ], msg, output, enc, retries)).run()
    except Exception:
      pass
    finally:
      self.socks[use] = False
    return bytes(output)


  def use(self):
    for port, used in self.socks.items():
      if not used:
        self.socks[port] = True
        return port
    return None
