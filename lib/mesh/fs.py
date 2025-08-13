def parse(file, handler, enc='utf-8'):
  raw = read(file, enc)
  if raw:
    return handler(raw)
  return None

def read(file, enc='utf-8'):
  try:
    with open(file, 'r', encoding=enc) as file:
      data = file.read()
    return data
  except Exception:
    return None

def save(file, data, handler, enc='utf-8'):
  raw = handler(data)
  if raw:
    return write(file, raw, enc)

def write(file, data, enc='utf-8'):
  try:
    with open(file, 'w', encoding=enc) as file:
      file.write(data)
    return True
  except Exception:
    return False


