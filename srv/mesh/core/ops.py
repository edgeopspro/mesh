from lib.mesh.utils import uid, uuid

addrs = {}
ops = {}

def reg(addr, tags):
  opid = uuid()
  addrs[opid] = addr
  for tag in tags:
    if not tag in ops:
      ops[tag] = []
    ops[tag].append(opid)
  return opid

def unreg(opid):
  if opid in addrs:
    del addrs[opid]
  for tag, opids in ops.items():
    index = opids.index(opid)
    if index > -1:
      del opids[index]

def run(mids, proc, msg):
  data = msg
  use = {}
  for tag in mids:
    if tag in ops:
      for opid in ops[tag]:
        if not opid in use:
          use[opid] = True
          addr = addrs[opid]
          if addr:
            ip, port = addr
            result = proc(ip, port, data)
            if isinstance(result, bytes):
              data = result
  return data