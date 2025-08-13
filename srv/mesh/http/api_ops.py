from lib.mesh.utils import uid
from srv.mesh.core.ops import reg, unreg

def start(ctx, input, heads, req):
  port = input['port'] if 'port' in input else None
  tags = input['tags'] if 'tags' in input else None
  if port and tags:
    return { 'opid': reg([req.client_address[0], port], tags) }
  raise Exception('invalid payload (both "port" and "tags" are required)')

def stop(ctx, input, heads, req):
  opid = heads['MESH-OPID'] if 'MESH-OPID' in heads else None
  if opid:
    unreg(opid)
    return {}
  raise Exception('invalid MESH-OPID header')

def use(router):
  prefix = '/mesh/ops/'
  router[prefix + 'start'] = start
  router[prefix + 'stop'] = stop
