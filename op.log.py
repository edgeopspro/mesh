from json import dumps
from time import time

from lib.mesh.fs import read
from lib.mesh.parsers.http import mid_json_in, mid_raw_out
from op.run import http

def live(ctx, key):
  if key == 'heartbeat':
    return "stayin' alive (log op)"

def proc_http(ctx, state):
  ctx.log('process incoming http payload')
  payload, heads, info = state
  base = ctx.data['website']
  return [ 
    read(f'{base}/view.html', enc='ascii'),
    { 
      'Content-Type': 'text/html; charset=utf-8'
    }, 
    { 'status': 200 }
  ]

def proc_live(ctx, state):
  ctx.log('process incoming live message')
  ctx.log(state)

def router(ctx, state):
  payload, heads, info = state
  status = info['status'] if 'status' in info else None
  if status and status == 200:
    proc_live(ctx, mid_json_in(ctx, state, parse=True))
  else:
    return proc_http(ctx, state)
  
def start(ctx):
  ctx.log(f'getting ready')
  tcp = ctx.services['tcp']
  ctx.data['website'] = ctx.config['use']['static']
  ctx.log(f'operator is ready (using port {tcp.port})')
  return True

def stop(ctx):
  ctx.log('bye bye')
  
http(
  [ start, live, stop ],
  [
    router,
    mid_raw_out
  ],
  'op.log.config.json'
)