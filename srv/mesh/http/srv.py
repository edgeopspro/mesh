from copy import deepcopy
from json import dumps, loads
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from socketserver import TCPServer
from traceback import print_exc

from lib.mesh.parsers.http import http_res, http_router, json_in, json_out
from lib.mesh.parsers.tcp_http import read_http_in, read_http_out
from lib.mesh.task import Task
from lib.mesh.utils import uid
from srv.mesh.core import ops
from srv.mesh.core.transporters.tcp import TCP
from srv.mesh.http import api_ops

context = None
router = None
tcp = None

class Server(BaseHTTPRequestHandler):
  def __init__(self, req, client_addr, srv):
    self.server_version = 'mesh.http.server/0.1'
    super().__init__(req, client_addr, srv)

  def do_DELETE(self):
    self.proc('DELETE')

  def do_GET(self):
    self.proc('GET')

  def do_PATCH(self):
    self.proc('PATCH')
  
  def do_POST(self):
    self.proc('POST')

  def do_PUT(self):
    self.proc('PUT')
  
  def log_message(self, format, *args):
    return

  def proc(self, method):
    data=None
    heads = self.headers
    info = {}
    input = None
    output = None
    payload = None
    path = self.path
    status = 0
    try:
      if not method in [ 'CONNECT', 'HEAD', 'GET', 'OPTIONS', 'TRACE' ]:
        length = heads.get('Content-Length')
        if length:
          input = self.rfile.read(int(length))
      route, origin = context.route(path, 'http')
      if not route:
        status = 404
        output = f'entry point "{self.path}" not found'
        self.send_error(status, output)
        data = { 'ok': False, 'payload': output }
      else:
        data = { 'heads': dict(heads), 'method': method, 'origin': origin, 'path': path, 'payload': input }
        status = 200
        if callable(route):
          output = route(context, json_in(input, force=True), heads, self)
          heads = {}
          payload, heads, info = http_res(output, heads, info)
          payload, heads = json_out(payload, heads, force=False)
        else:
          tcp = context.services['tcp_socks']
          pre, proc, post = route
          msg = read_http_in(data)
          ops.run(pre, tcp.fnf, msg)
          heads, output, info = read_http_out(ops.run(proc, tcp.snr, msg))
          payload, heads, info = http_res(output, heads, info)
          if 'status' in info:
            status = info['status']
          payload, heads = json_out(payload, heads, force=False)
          data = { 'req': data, 'res': { 'heads': heads, 'payload': output, 'status': status } }
          msg = read_http_in(data)
          ops.run(post, tcp.fnf, msg)
        self.send_response(status)
        for name, value in heads.items():
          self.send_header(name, value)
        if not isinstance(payload, bytes):
          if payload:
            if not isinstance(payload, str):
              payload = str(payload)
            payload = bytearray(str(payload).encode('utf-8'))
        if payload:
          self.send_header('Content-Length', len(payload))
        self.end_headers()
        if payload:
          self.wfile.write(payload)
        data['ok'] = True
    except Exception as error:
      status = 500
      payload = str(error)
      self.send_error(status, payload)
      if context.conf('debug'):
        print_exc()
      data = { 'ok': False, 'payload': payload }
    finally:
      if data:
        context.log(data)


def start(ctx):
  def load_srv(req, client_addr, srv):
    thread = Thread(target=Server, name='http_handler', args=(req, client_addr, srv), daemon=True)
    thread.start()
    while thread.is_alive(): 
      thread.join(1)

  global context, router
  
  ctx.log('starting mesh http service')
  ctx.log('using config:')
  ctx.log(ctx.config)
  ctx.log('using routes:')
  ctx.log(ctx.router)
  context = ctx
  router = http_router(ctx.router['http'] if 'http' in ctx.router else {})
  srv = ctx.reg('http_srv', lambda config: ThreadingHTTPServer(('', config['port']), Server))
  tcp = ctx.reg('tcp_socks', lambda config: TCP(config['ports']))
  api_ops.use(router)
  Task(srv.serve_forever, ()).run()


def stop(ctx):
  ctx.log('stopping mesh http service...')
  ctx.use('http_srv', lambda service: service.shutdown())
  ctx.log('bye bye')