from socket import socket, AF_INET, SOCK_STREAM
from time import sleep

from lib.mesh.task import Task
from lib.mesh.parsers.tcp import msg

def connect(handler, retries=10):
  ok = False
  interval = 1
  sock = socket(AF_INET, SOCK_STREAM)
  while not ok and retries > 0:
    try:
      handler(sock)
      ok = True
    except Exception as error:
      print('xxxx', error)
      ok = False
      sleep(interval)
      interval += 1
      retries -= 1
  return sock if ok else None

def send(ip, ports, data, enc, retries):
  source, target = ports
  sock = connect(lambda sock: sock.connect((ip, int(target))), retries)
  if not sock:
    raise Exception(f'unable to connect {ip}:{target}')
  sock.send(msg(data, [ source, enc ]))
  sock.close()

def receive(port, retries, buffer):
  sock = connect(lambda sock: sock.bind(('', int(port))), retries)
  if not sock:
    raise Exception(f'unable to bind to local port {port}')
  encoding = 'ascii'
  heads = None
  init = True
  result = bytearray()
  sock.listen(1)
  connection, info = sock.accept()
  data = True
  while data:
    raw = connection.recv(buffer)
    if init:
      init = False
      data = raw.decode(encoding)
      head, body = data.split(' ', 1)
      size, source, enc = head.split('.')
      heads = [ int(size), source, enc ]
      result.extend(body.encode(enc))
    else:
      if len(result) < heads[0]:
        result.extend(raw)
      else:
        break
  sock.close()
  enc = heads[2]
  return [ heads, result if enc == encoding else result.decode(enc) ]

class BasicTCP():
  def fnf(self, ip, port, data, enc='utf-8', retries=10):
    return Task(send, (ip, [ 0, port ], data, enc, retries)).run()

