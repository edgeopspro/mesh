def msg(data, head=[]):
  if not data:
    data = b''
  header = '.'.join(map(str, [ len(data) ] + head))
  msg = bytearray(f'{header} '.encode('ascii'))
  msg.extend(data)
  return msg