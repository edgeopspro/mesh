from json import dumps, loads
from traceback import print_exc

from lib.mesh.task import BackgroundTask
from lib.mesh.parsers.stream import write_json_stream
from lib.mesh.parsers.tcp_http import validate_http_state, write_http_in, write_http_out

hooks = {}
main = None
tasks = []

def start(ctx):
  global hooks, main, tasks

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
      payload = res['payload']
      opid = heads['MESH-OPID'] = payload['opid']
      secret = payload['secret']
      stream = payload['stream']
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
          tcp.rns(secret, enc='ascii', handlers=[ write_http_in, validate_http_state, write_http_out ])
        ]
        if stream:
          conf = ctx.conf([ 'mesh', 'op', 'stream' ])
          if isinstance(conf, dict):
            for key, streamer in conf.items():
              if key:
                interval = streamer['interval'] if 'interval' in streamer else None
                tags = streamer['tags'] if 'tags' in streamer else None
                if interval and tags:
                  tasks.append(tcp.live(stream, interval, lambda: write_json_stream(opid, ctx.trigger(1, key), tags, secret)))
        main = tasks.pop(0)
        for task in tasks:
          task.run(wait=False)
        main.run()
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
  try:
    ctx.log('stopping operator')
    if 'stop' in hooks:
      hooks['stop']()
    if main:
      main.stop()
    for task in tasks:
      task.stop()
    ctx.trigger(2)
    ctx.lifecycle = None
  except Exception as error:
    print_exc()