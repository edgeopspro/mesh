from base64 import b64decode
from json import dumps, loads
from time import sleep

from lib.mesh.task import BackgroundTask, Task
from lib.mesh.utils import uid
from srv.mesh.core import live, ops
from srv.mesh.core.live import sub_http

def get_opid(heads):
  opid = get_value(heads, 'MESH-OPID')
  if not opid:
    raise Exception('invalid MESH-OPID header')
  return opid

def get_value(obj, key, fallback=None):
  return obj[key] if key in obj else fallback

def live(ctx, input, heads, req):
  enc = 'utf-8'
  heads = {
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Type': 'text/event-stream'
  }
  req.send_response_only(200)
  for key, value in heads.items():
    req.send_header(key, value)
  req.end_headers()
  sub_http(req)
  return [ {}, {}, { 'status': 0 } ]

def start(ctx, input, heads, req):
  port = get_value(input, 'port')
  stream = ctx.data['mesh_stream_port']
  tags = get_value(input, 'tags')
  if port and tags:
    opid, key = ops.reg([req.client_address[0], port], tags)
    return { 'opid': opid, 'secret': key, 'stream': stream }
  raise Exception('invalid payload (both "port" and "tags" are required)')

def stop(ctx, input, heads, req):
  opid = get_opid(heads)
  ops.unreg(opid)
  return {}

def use(router):
  prefix = '/mesh/ops/'
  router[prefix + 'live'] = live
  router[prefix + 'start'] = start
  router[prefix + 'stop'] = stop
