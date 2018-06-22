import multiprocessing

from gunicorn.six import iteritems
import gunicorn.app.base


class StandaloneApplication(gunicorn.app.base.BaseApplication):
  def __init__(self, wsgi_app, port, debug=False):
    self.port = port
    self.debug = debug
    self.wsgi_app = wsgi_app
    if self.debug:
      self.log_level = "debug"
    else:
      self.log_level = "info"
    self.num_workers = (multiprocessing.cpu_count() * 2) + 1

    self.options = {
        "bind":               "%s:%s" % ("0.0.0.0", self.port),
        "worker_class":       "gevent",
        "workers":            self.num_workers,
        "worker_connections": 100,
        "timeout":            60,
        "keepalive":          10,
        "loglevel":           self.log_level,
        "spew":               self.debug,
        "accesslog":          "-",
        "errorlog":           "-",
        "access_log_format":  '%(t)s %(h)s %(l)s %(u)s "%(r)s" %(s)s %(b)s %(L)s "%(f)s" "%(a)s"'
    }
    super(StandaloneApplication, self).__init__()

  def load_config(self):
    config = dict([(key, value) for (key, value) in iteritems(self.options)
                  if key in self.cfg.settings and value is not None])
    for key, value in iteritems(config):
      self.cfg.set(key.lower(), value)

  def load(self):
    return self.wsgi_app
