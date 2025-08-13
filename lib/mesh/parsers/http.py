from json import dumps, loads

def http_res(result, heads = {}, info={}):
  if isinstance(result, list) and len(result) == 3:
    payload, header, information = result
    if isinstance(header, dict):
      heads = { **heads, **header }
    if isinstance(information, dict):
      info = { **info, **information }
  else:
    payload = result
  return payload, heads, info

def http_router(router):
  postfix = '[\?|\/](.+)?'
  routes = {}
  for key, handler in router.items():
    pattern = key.replace('/', '\/').replace('*', '.+')
    routes[f'{pattern}{postfix}'] = [ key, handler ]
  for key, entry in routes.items():
    origin, handler = entry
    router[key] = { 'origin': origin, 'use': handler }
  return router

def json_in(payload, force=False):
  try:
    return loads(payload)
  except Exception as error:
    return {} if force else payload

def json_out(payload, heads={}, force=False):
  if isinstance(payload, dict) or isinstance(payload, list):
    try:
      payload = dumps(payload)
      heads['Content-Type'] = 'application/json'
    except Exception:
      if force:
        payload = None 
  return payload, heads

def mid_json_in(ctx, state, force=True):
  heads, payload, info = state
  return [ json_in(payload, force), heads, info ]

def mid_json_out(ctx, state, force=True):
  payload, heads, info = http_res(state)
  payload, heads = json_out(payload, heads, force)
  return { 'heads': heads, 'info': info, 'payload': payload }

def mid_raw_out(ctx, state):
  payload, heads, info = http_res(state)
  return { 'heads': heads, 'info': info, 'payload': payload }