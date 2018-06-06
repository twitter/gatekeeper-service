import multiprocessing

from gunicorn.six import iteritems
import gunicorn.app.base


class StandaloneApplication(gunicorn.app.base.BaseApplication):
  def __init__(self, wsgi_app, port, options={}, debug=False):
    self.port = port
    self.options = options
    self.debug = debug
    self.wsgi_app = wsgi_app
    if self.debug:
      self.log_level = "debug"
    else:
      self.log_level = "info"

    self.num_workers = (multiprocessing.cpu_count() * 2) + 1

    self.options = {
        'bind': '%s:%s' % ('0.0.0.0', self.port),
        'workers': self.num_workers,
        'worker_class': 'gevent',
        'worker_connections': 100,
        'threads': self.num_workers,
        'keepalive': 10,
        'accesslog': '-',  # '-' means log to stderr.
        'errorlog': '-',   # '-' means log to stderr.
        'enable_stdio_inheritance': True,
        'access_log_format': '%(t)s %(h)s %(l)s %(u)s "%(r)s" %(s)s %(b)s %(L)s "%(f)s" "%(a)s"',
        'loglevel': self.log_level,
        'spew': True,
        'timeout': 60,
    }
    super(StandaloneApplication, self).__init__()

  def load_config(self):
    config = dict([(key, value) for (key, value) in iteritems(self.options)
                  if key in self.cfg.settings and value is not None])
    for key, value in iteritems(config):
      self.cfg.set(key.lower(), value)

  def load(self):
    return self.wsgi_app
