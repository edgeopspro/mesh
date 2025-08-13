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