from threading import current_thread, Thread
from time import sleep

class Task():
  def __init__(self, handler, args):
    self.thread = Thread(target=handler, args=args)

  def run(self):
    self.thread.start()
    while self.thread.is_alive(): 
      self.thread.join(1)
    return self.thread

  def stop(self):
    if self.thread:
      self.thread.join()


class BackgroundTask(Task):
  def __init__(self, handler, args, interval=0):
    def proc(handler, args, interval):
      while True:
        handler(**args)
        if interval > 0:
          sleep(interval)

    super().__init__(proc, (handler, args, interval))