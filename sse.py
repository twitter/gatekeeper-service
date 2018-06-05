class ServerSentEvent(object):

  def __init__(self, data):
    self.data = data
    self.event = None
    self.id = None
    self.desc_map = {
      self.data: "data",
      self.event: "event",
      self.id: "id"
    }

  def encode(self):
    if not self.data:
      return ""
    lines = ["%s: %s" % (v, k)
             for k, v in iter(self.desc_map.items()) if k]

    return "%s\n\n" % "\n".join(lines)
