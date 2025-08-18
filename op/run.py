from op.mesh.core.ctx import Context
from op.mesh.http import op

def http(cyc, mids, conf):
  ctx = Context(cyc, mids, conf)

  try:
    op.start(ctx)
  except SystemExit:
    op.stop(ctx)
  except KeyboardInterrupt:
    op.stop(ctx)