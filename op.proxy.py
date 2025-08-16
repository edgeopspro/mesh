from json import dumps
from time import time

from lib.mesh.fs import read
from lib.mesh.parsers.http import mid_raw_out
from op.run import http

mimes = {
  'css': 'text/css',
  'html': 'text/html',
  'js': 'application/javascript',
  'svg': 'image/svg+xml'
}

def live(ctx, key):
  if key == 'heartbeat':
    return "stayin' alive (proxy op)"

def proc_http(ctx, state):
  ctx.log('process incoming http payload')
  payload, heads, info = state
  base = ctx.data['website']
  method = info['method']
  origin = info['origin']
  path = info['path'][len(origin):]
  if not path:
    path = '/index.html'
  extension = path.split('.').pop()
  ctx.log(f'{method} {path} {heads} {payload}')
  content = read(f'{base}{path}', enc='ascii')
  if content:
    return [ 
      content,
      { 
        'Content-Type': mimes[extension] if extension in mimes else 'text/plain'
      }, 
      { 'status': 200 }
    ]
  else:
    return [ '', {}, { 'status': 404 } ]


def start(ctx):
  ctx.log(f'getting ready')
  tcp = ctx.services['tcp']
  ctx.data['website'] = ctx.config['use']['static']
  ctx.log(f'operator is ready (using port {tcp.port})')
  return True


def stop(ctx):
  ctx.log('bye bye')
  # do some cleanup maybe
  
http(
  [ start, live, stop ],
  [ proc_http, mid_raw_out ],
  'op.proxy.config.json'
)