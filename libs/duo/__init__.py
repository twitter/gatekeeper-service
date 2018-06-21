import base64

import duo_client


class DuoAdminApi(object):
  def __init__(self, config=None, use_proxy=False, proxy_config=None):
    self.config = config
    self.use_proxy = use_proxy
    self.proxy_config = proxy_config
    self.admin_api = self._create_duo_client()

  def _create_duo_client(self):
    """
    Creates a DUO Admin API Client object.
    :return: DUO client object
    """
    if self.config["ca_certs"] == "":
      client = duo_client.Admin(ikey=self.config["ikey"],
                                skey=self.config["skey"],
                                host=self.config["host"])
    else:
      client = duo_client.Admin(ikey=self.config["ikey"],
                                skey=self.config["skey"],
                                host=self.config["host"],
                                ca_certs=self.config["ca_certs"])

    if self.use_proxy is True:
      self.proxy_headers = {"Proxy-Authorization": "Basic " + base64.b64encode(b"%s:%s" % (
                            self.proxy_config["proxy_user"],
                            self.proxy_config["proxy_pass"])).decode("utf-8")}

      client.set_proxy(host=self.proxy_config["proxy_url"],
                       port=self.proxy_config["proxy_port"],
                       headers=self.proxy_headers,
                       proxy_type="CONNECT")
    return client

  def list_users(self):
    """
    List of all users.
    :return: list of user objects.
    """
    r = self.admin_api.get_users()
    return r

  def get_user(self, username):
    """
    Return a single user object by username.
    :param: username: username
    :return: user object.
    """
    try:
      r = self.admin_api.get_users_by_name(username)
      return r
    except AttributeError as e:
      return "Error connecting to Duo: %s" % e

  def delete_user(self, user_id):
    """
    Delete user by id.
    :param: user_id: user_id
    :return: empty string when successful
    """
    r = self.admin_api.delete_user(user_id)
    if r == "":
      return True
    else:
      return False

  def remove_from_duo(self, username):
    """
    Delete user by username.
    :param: username: username
    :return: Bool
    Note: This returns a bool to show user was deleted.
    """
    try:
      result = None
      user = username.split('@')[0]
      user_data = self.get_user(user)
      if len(user_data) == 0:
        result = True
      elif user_data is not None:
        for item in user_data:
          if item["username"] == user:
            user_id = item["user_id"]
            if self.delete_user(user_id) is True:
              result = True
      else:
        result = False
      return result

    except(AttributeError, KeyError):
      return "Error connecting to Duo."
