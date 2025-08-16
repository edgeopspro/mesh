from json import dumps
from time import time

from lib.mesh.parsers.http import mid_json_in, mid_json_out
from op.run import http

def live(ctx, key):
  if key == 'heartbeat':
    return "stayin' alive (simple op)"

def proc_http(ctx, state):
  ctx.log('process incoming http payload')
  payload, heads, info = state
  origin = info['origin']
  path = info['path']
  ctx.log(f'received payload {payload} of type: {type(payload)} from origin {origin} (with path {path})')
  return {
    'test': 'this',
    'and also this': time()
  }

def start(ctx):
  ctx.log(f'getting ready')
  tcp = ctx.services['tcp']
  # do some initialization here
  ctx.log(f'operator is ready (using port {tcp.port})')
  return True


def stop(ctx):
  ctx.log('bye bye')
  # do some cleanup maybe
  
http(
  [ start, live, stop ],
  [ 
    mid_json_in,
    proc_http,
    mid_json_out
  ],
  'op.simple.config.json'
)