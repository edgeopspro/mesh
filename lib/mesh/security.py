def parse_byte(byte, key, index, direction=1):
  max = 127
  offset = ord(key[index % len(key)])
  byte = byte + offset * direction
  if direction > 0 and byte > max:
    byte -= max
  elif direction < 0 and byte < 0:
    byte += max
  return byte

def encode(value, key):
  encoded = bytearray()
  for index, byte in enumerate(value):
    encoded.append(parse_byte(byte, key, index, 1))
  return encoded

def decode(value, key):
  decoded = bytearray()
  for index, char in enumerate(value):
    decoded.append(parse_byte(ord(char) if isinstance(char, str) else char, key, index, -1))
  return bytes(decoded)