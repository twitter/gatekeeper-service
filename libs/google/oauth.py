import socks
from httplib2 import Http, HttpLib2ErrorWithResponse, ProxyInfo
from oauth2client.service_account import ServiceAccountCredentials


class GoogleOAuthApi(object):

  def __init__(self, config):
    self.config = config
    self.SCOPES = self.config["google_apps"]["api_scopes"]
    self.proxy_info = None
    if self.config["defaults"]["http_proxy"]["use_proxy"]:
      self._PROXY_HOST = self.config["defaults"]["http_proxy"]["proxy_url"]
      self._PROXY_PORT = self.config["defaults"]["http_proxy"]["proxy_port"]
      self._PROXY_USER = self.config["defaults"]["http_proxy"]["proxy_user"]
      self._PROXY_PASS = self.config["defaults"]["http_proxy"]["proxy_pass"]
      self.proxy_info = ProxyInfo(proxy_type=socks.PROXY_TYPE_HTTP,
                                  proxy_host=self._PROXY_HOST,
                                  proxy_port=self._PROXY_PORT,
                                  proxy_user=self._PROXY_USER,
                                  proxy_pass=self._PROXY_PASS)
    self.credentials = self._get_credentials()

  def _get_credentials(self):
    """
    Gets valid user credentials from storage.
    :return:
      credentials, the obtained credentials.
    """
    credentials_file = self.config["google_apps"]["credentials_keyfile"]
    credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_file,
                                                                   scopes=self.SCOPES)
    if not credentials or credentials.invalid:
      print('Credentials are invalid!')
    return credentials

  def get_oauth_token(self, delegated_user):
    """
    Authorizes the credentials read from storage with the google oauth api servers.
    :param delegated_user, user email to delegate access to.
    :return:
      oauth, the authorized oauth token.
    """
    oauth = None
    try:
      delegated_credentials = self.credentials.create_delegated(delegated_user)
      oauth = delegated_credentials.authorize(Http(proxy_info=self.proxy_info))
    except HttpLib2ErrorWithResponse as e:
      print("Error building a connector to the service: %s" % e)
    return oauth
