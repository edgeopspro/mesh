from json import dumps, loads

from lib.mesh.parsers.http import json_out
from lib.mesh.parsers.tcp import msg

header_encoding = 'ascii'

def read_http_msg(msg):
  values = msg.split(b' ', 1)
  if not values or len(values) == 0 or len(values[0]) == 0:
    return [ {}, b'', {} ]
  size, body = values
  queue = list(map(int, size.split(b'.')))
  results = []
  start = 0
  stop = 0
  while len(queue) > 0:
    stop += queue.pop()
    results.append(body[start:stop])
    stop += 1
    start = stop
  info, heads, payload = results
  return [
    loads(heads.decode(header_encoding)) if heads else {},
    payload if payload else b'',
    loads(info.decode(header_encoding)) if info else {}
  ]
  
def write_http_msg(state):
  def pack(data, extra=[]):
    return bytes(msg(data.encode(header_encoding), extra)).decode(header_encoding)

  def use(prop, target=None, fallback=None):
    value = state[prop] if prop in state else fallback
    if isinstance(target, dict):
      target[prop] = value
    else:
      return value

  heads = use('heads', None, {})
  payload = use('payload', None, b'')
  if 'info' in state:
    info = state['info']
  else:
    info = {}
    use('method', info)
    use('origin', info)
    use('path', info)
  if isinstance(payload, bytearray):
    payload = bytes(payload)
  elif isinstance(payload, str):
    payload = payload.encode(header_encoding)
  return msg(payload, [ pack(dumps(heads), [ pack(dumps(info)) ]) ])

def read_http_in(state):
  return write_http_msg(state)

def read_http_out(msg):
  return read_http_msg(msg)

def write_http_in(msg):
  return read_http_msg(msg.encode(header_encoding) if isinstance(msg, str) else msg)

def write_http_out(state):
  return write_http_msg(state)

def validate_http_state(state):
  return state if state and 'payload' in state and state['payload'] else None