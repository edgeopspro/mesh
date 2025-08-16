def http_router(router, base={}):
  postfix = '[\?|\/](.+)?'
  routes = {}
  for key, handler in router.items():
    pattern = key.replace('/', '\/').replace('*', '.+')
    routes[f'{pattern}{postfix}'] = [ key, handler ]
  for key, entry in routes.items():
    origin, handler = entry
    router[key] = { 'origin': origin, 'use': handler }
  return router

def stream_router(router):
  return { 'origin': 'live', 'use': router }