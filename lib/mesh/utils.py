from datetime import datetime
from sys import stdout
from time import time, sleep
from uuid import uuid4

def log(key, something):
  msg = str(something)
  time = utc()
  stdout.write(f'{key}  {time}  {msg}\n')

def ts():
  return time()

def uid():
  return uuid().split('-')[0]

def uuid():
  return str(uuid4())

def utc():
  return datetime.utcnow()

def wait(interval, until):
  while until():
    sleep(interval)

