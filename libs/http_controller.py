import requests


class HttpController(object):
  def __init__(self, base_url, use_proxy=False, proxy_config=None,
               max_retries=3, timeout_secs=10):
    self.base_url = base_url
    self.use_proxy = use_proxy
    self.max_retries = max_retries
    self.timeout_secs = timeout_secs
    if self.use_proxy is True:
      self.proxy_config = proxy_config
      self.proxy_info = self._get_proxy_info()
    else:
      self.proxy_info = None

  def _get_proxy_info(self):
    """
    Retrieve Proxy Config settings
    :return: proxy_info dict
    """
    proxy_info = {
      "http": "http://{proxy_user}:{proxy_pass}@{proxy_url}:{proxy_port}"
              .format(**self.proxy_config),
      "https": "https://{proxy_user}:{proxy_pass}@{proxy_url}:{proxy_port}"
              .format(**self.proxy_config)
    }
    return proxy_info

  def api_request(self, method, endpoint, response_type="json", **kwargs):
    """
    Generic REST API Controller.
    """
    r = None
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=self.max_retries)
    api_endpoint = self.base_url + endpoint
    session.mount(api_endpoint, adapter)
    try:
      r = getattr(session, method)(url=api_endpoint,
                                   timeout=self.timeout_secs,
                                   proxies=self.proxy_info, **kwargs)
    except (requests.exceptions.ConnectionError, requests.exceptions.RequestException,
            AttributeError, TypeError) as e:
      print(e)
    if response_type == "json":
      return r.json()
    elif response_type == "text":
      return r.text
    elif response_type == "xml":
      return r.content
