import time

from Crypto import Random
from twitter.common import log

from google.admin import GoogleAdminApi
from google.calendar import GoogleCalendarApi
from google.drive import GoogleDriveApi
from google.gmail import GoogleGmailApi
from google.oauth import GoogleOAuthApi
from helper_functions import HelperFunctions
from ldap_client import LDAPClient
from pagerduty import PagerDutyApi
from duo import DuoAdminApi

config = HelperFunctions().read_config_from_yaml()

NO_SUSPEND_ACTIONS = ["remove_from_oncalls", "org_unit_reset"]


class Runner(object):
  def __init__(self, user=None):
    Random.atfork()
    self.ADMIN_USER = config["google_apps"]["admin_user"]
    self.DOMAIN = config["google_apps"]["domain"]
    self.use_proxy = config["defaults"]["http_proxy"]["use_proxy"]

    self.user = user
    self.admin_email = "%s@%s" % (self.ADMIN_USER, self.DOMAIN)
    self.user_email = "%s@%s" % (user, self.DOMAIN)

    self.google_oauth = GoogleOAuthApi(config=config)
    self.oauth_admin = self.google_oauth.get_oauth_token(self.admin_email)
    self.oauth_user = self.google_oauth.get_oauth_token(self.user_email)

    self.admin_api = GoogleAdminApi(self.oauth_admin, config=config["google_apps"])
    self.gmail_api = GoogleGmailApi(self.oauth_user)
    self.drive_api = GoogleDriveApi(self.oauth_user)
    self.calendar_api = GoogleCalendarApi(self.oauth_user)

    self.ldap_client = LDAPClient(config=config["ldap"])

    self.is_valid_user = self._is_valid_user()
    self.is_suspended_user = self._is_suspended_user()

    self.pagerduty_api = PagerDutyApi(config=config["pagerduty"],
                                      use_proxy=self.use_proxy,
                                      proxy_config=config["defaults"]["http_proxy"])

    self.duo_api = DuoAdminApi(config=config["duo"],
                               use_proxy=self.use_proxy,
                               proxy_config=config["defaults"]["http_proxy"])

  def _is_valid_user(self):
    """
    Checks whether the user is a valid LDAP user.
    :return: bool
    Note: Additional check now makes sure the user's name on LDAP matches than on Google Apps.
    """
    name_on_gapps = ""
    is_valid = self.ldap_client.is_valid_user(user=self.user)
    user_info = self.ldap_client.get_user_info(user=self.user)
    name_on_ldap = user_info["sn"][0]
    if self.oauth_admin is not None:
      try:
        name_on_gapps = ("{familyName}"
                         .format(**self.admin_api.get_user_name(self.user_email)))
      except (TypeError, UnicodeEncodeError) as e:
        log.info("is_valid: %s" % e)
    log.info("user: %s - is_valid: %r - name_on_ldap: %s - name_on_gapps: %s" %
             (self.user, is_valid, name_on_ldap, name_on_gapps))
    if is_valid and name_on_ldap == name_on_gapps:
      return True
    else:
      return False

  def _is_suspended_user(self):
    """
    Checks whether the user is suspended.
    :return: bool
    """
    is_suspended = False
    if self.is_valid_user:
      is_suspended = self.admin_api.is_suspended(self.user_email)
    log.info("user: %s - is_suspended: %r" % (self.user, is_suspended))
    return is_suspended

  def suspend_user(self, suspend):
    """
    Suspends or un-suspends a user.
    :param: suspend: bool
    """
    msg = ""
    if self.is_valid_user:
      if suspend and self._is_suspended_user():
        msg = "%s - User already suspended" % self.user
      elif suspend and not self._is_suspended_user():
        self.admin_api.suspend(self.user_email)
        msg = "%s - User was suspended" % self.user
      elif not suspend and self._is_suspended_user():
        self.admin_api.un_suspend(self.user_email)
        while self._is_suspended_user():  # workaround for google api delays in propagation
          time.sleep(8)
        msg = "%s - User was un-suspended" % self.user
      elif not suspend and not self._is_suspended_user():
        msg = "%s - User already un-suspended" % self.user
    else:
      msg = "%s - Not a valid LDAP user" % self.user
    log.info(msg)
    return msg

  def perform_action(self, api_connector, action, kwargs):
    """
    Performs offboarding actions selected from the Web UI form.
    :param api_connector: string of the API connector to use
    :param action: name of action to be performed
    :return: msg log for action performed, along with status
    Note: action item must match function names of the equivalent API class.
    """
    msg = ""
    if self.is_valid_user:
      if self.is_suspended_user and action not in NO_SUSPEND_ACTIONS:
        self.suspend_user(False)
      connector = getattr(self, api_connector)
      result = getattr(connector, action)(self.user_email, **kwargs)

      if type(result) is dict:
        results = []
        for k, v in result.items():
          if v is True:
            results.append("<span class='text-success'>%s</span>" % k)
          elif v is False:
            results.append("<span class='text-danger'>%s</span>" % k)
          else:
            results.append(k)
        if not results:
          results = "<span class='text-success'>SUCCESS</span>"
        msg = "<p>%s: %s</p>" % (action.replace("_", " ").upper(), results)
      else:
        if result is False:
          msg_color = "danger"
          msg_text = "FAILED"
        elif result is True:
          msg_color = "success"
          msg_text = "SUCCESS"
        elif result is None:
          msg_color = "danger"
          msg_text = "FAILED (EMPTY RESULT)"
        else:
          msg_color = "success"
          msg_text = "SUCCESS"
        msg = ("<p>%s: <span class=\"text-%s\">%s</span></p>" %
               (action.replace("_", " ").upper(), msg_color, msg_text))
    else:
      msg = "<p><span class=\"text-danger\">FAILED - INVALID USER</span></p>"
    log.info(msg)
    return msg
