from subprocess import PIPE, Popen

from srv.mesh.core.ctx import Context
from srv.mesh.http import srv

def http(config, router):
  ctx = Context(config, router)
  try:
    srv.start(ctx)
  except SystemExit:
    srv.stop(ctx)
  except KeyboardInterrupt:
    srv.stop(ctx)

def https(config):
  ctx = Context(config, None)
  srvs, http, https, host, port = [ 'services', 'http_srv', 'https_srv', 'host', 'port' ]
  http_port = ctx.conf([ srvs, http, port ])
  https_port = ctx.conf([ srvs, https, port ])
  if http_port and https_port:
    host = ctx.conf([ srvs, http, host ])
    if not host:
      host = 'localhost'
    try:
      cmd = [
        'bin/caddy',
        'reverse-proxy',
        '--from',
        f'{host}:{https_port}',
        '--to',
        f':{http_port}'
      ]
      proc = Popen(cmd, stdout=PIPE, text=True)
      for line in proc.stdout:
        print(line)
      proc.wait()
    except SystemExit:
      pass
    except KeyboardInterrupt:
      pass
    finally:
      print('bye bye')
  else:
    print('unable to resolve both "http_srv" and "https_srv" ports')