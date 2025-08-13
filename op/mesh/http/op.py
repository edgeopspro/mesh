from json import dumps, loads
from traceback import print_exc

from lib.mesh.task import BackgroundTask
from lib.mesh.parsers.tcp_http import write_http_in, write_http_out

hooks = {}
tasks = []

def start(ctx):
  global hooks, tasks

  if ctx.trigger(0):
    heads = {}
    http = ctx.services['http']
    tcp = ctx.services['tcp']
    res = http.fetch(
      {
        'path': 'start',
        'payload': { 'port': tcp.port, 'tags': ctx.setup['op']['tags'] }
      },
      dumps,
      loads
    )
    if res['ok']:
      opid = heads['MESH-OPID'] = res['payload']['opid']
      hooks['stop'] = lambda: http.fetch(
        {
          'path': 'stop',
          'heads': heads
        },
        dumps,
        loads
      )
      try:
        ctx.log(f'operator id by mesh server {opid}')
        tasks = [
          tcp.rns(enc='ascii', handlers=[ write_http_in, write_http_out ])
        ]
        for task in tasks:
          task.run()
      except SystemExit:
        ctx.log('exit signal initiated by system')
        stop(ctx)
      except KeyboardInterrupt:
        ctx.log('exit signal initiated by user')
        stop(ctx)
      except Exception as error:
        ctx.log(error)
        print_exc()
    else:
      ctx.log('unable to register operator')
  else:
    ctx.log('operator is not ready')
    stop(ctx)

def stop(ctx):
  ctx.log('stopping operator')
  if 'stop' in hooks:
    hooks['stop']()
  for task in tasks:
    task.stop()
  ctx.trigger(1)
  ctx.lifecycle = None