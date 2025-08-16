from json import dumps
from http.client import HTTPConnection
from traceback import print_exc

from lib.mesh.utils import ts

def fetch(input, config={}):
  def use(prop):
    return input[prop] if prop in input else config[prop] if prop in config else None
  
  heads = {}
  method = None
  ok = True
  payload = None
  port = None
  start = ts()
  status = 0
  url = None
  try:
    method = use('method')
    url = [ use('host'), use('path') ]
    sections = url[0].split(':')
    host = sections[0]
    if len(sections) == 2:
      port = sections[1]
    base = use('base')
    timeout = use('timeout')
    if base:
      path = url[1]
      url[1] = f'{base}/{path}'
    connection = HTTPConnection(host, port, timeout=timeout)
    heads = { 
      **(input['heads'] if 'heads' in input else {}),
      **(config['heads'] if 'heads' in config else {})
    }
    payload = input['payload'] if 'payload' in input else None
    heads['Content-Length'] = len(payload) if payload else 0
    connection.request(
      method,
      url[1],
      body = payload,
      headers = heads
    )
    heads = {}
    res = connection.getresponse()
    status = res.status
    for name, value in res.getheaders():
      heads[name] = value
    payload = res.read()
  except Exception as error:
    ok = False
    status = 500
    payload = str(error)
    print_exc()
  output = {
    'tags': [ 'http' ],
    'url': url,
    'method': method,
    'status': status,
    'duration': ts() - start,
    'heads': heads
  }
  return { **output, **{ 'ok': ok, 'payload': payload } }


def webhook(path, payload, host=None, heads={}):
  if path and payload:
    if not isinstance(heads, dict):
      heads = {}
    heads['Content-Type'] = 'application/json'
    return fetch({
      'method': 'POST',
      'host': host if host else 'localhost',
      'path': path,
      'payload': dumps(payload)
    })