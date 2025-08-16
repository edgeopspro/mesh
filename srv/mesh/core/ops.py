from secrets import token_urlsafe

from lib.mesh.security import encode, decode
from lib.mesh.utils import uid, uuid

addrs = {}
keys = {}
ops = {}

def parse(data, opid):
  key = keys[opid] if opid in keys else None
  if key:
    return decode(data, key)
  return None

def reg(addr, tags, key_size=32):
  opid = uuid()
  key = token_urlsafe(key_size)
  addrs[opid] = addr
  keys[opid] = key
  for tag in tags:
    if not tag in ops:
      ops[tag] = []
    ops[tag].append(opid)
  return [ opid, key ]

def unreg(opid):
  if opid in addrs:
    del addrs[opid]
  for tag, opids in ops.items():
    try:
      index = opids.index(opid)
      if index > -1:
        del opids[index]
    except Exception:
      pass

def run(mids, proc, msg, fmt=encode):
  data = msg
  use = {}
  for tag in mids:
    if tag in ops:
      for opid in ops[tag]:
        if not opid in use:
          use[opid] = True
          addr = addrs[opid] if opid in addrs else None
          key = keys[opid] if opid in keys else None
          if addr and key:
            ip, port = addr
            result = proc(ip, port, fmt(data, key))
            if isinstance(result, bytes):
              value = parse(result, opid)
              if value:
                data = value
  return data