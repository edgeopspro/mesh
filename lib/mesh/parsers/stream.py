from base64 import b64decode, b64encode
from json import dumps, loads

from lib.mesh.parsers.tcp_http import write_http_out
from lib.mesh.security import encode, decode
from lib.mesh.utils import ts

encoding = 'utf-8'

def mid_json_out(payload, secret):
  return write_http_out({
    'payload': read_json_stream(payload, secret),
    'heads': { 'Content-Type': 'application/json' },
    'info': { 'status': 200 }
  })

def read_json_stream(payload, secret):
  try:
    data = loads(payload)
    value = data['value'] if 'value' in data else None
    if value:
      data['value'] = decode(b64decode(value.encode('ascii')), secret).decode(encoding)
    return dumps(data).encode(encoding)
  except Exception:
    return None

def sign_json_payload(payload):
  try:
    data = loads(payload.decode(encoding))
    opid = data['opid'] if 'opid' in data else None
    ts = data['ts'] if 'ts'in data else None
    return [ f'{opid}_{ts}', opid, ts ]
  except Exception:
    return [ None, None, None ]


def write_json_stream(opid, value, tags, secret):
  ok = True
  if value:
    try:
      value = dumps(value)
    except Exception:
      value = str(value)
  try:
    value = b64encode(encode(value.encode(encoding), secret)).decode(encoding) if value else None
  except Exception as error:
    value = str(error)
    ok = False
  data = { 
    'ts': ts(),
    'opid': opid,
    'ok': ok,
    'tags': tags,
    'value': value
  }
  return dumps(data).encode(encoding)