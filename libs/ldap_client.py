import ldap
from ldap.ldapobject import ReconnectLDAPObject
from ldap.resiter import ResultProcessor

from threading import Timer


class LDAPClient(ReconnectLDAPObject, ResultProcessor, object):
  def __init__(self, config):
    self.config = config
    super(LDAPClient, self).__init__(uri=self.config["uri"])
    self.base_dn = self.config["base_dn"]
    ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_ALLOW)

  def ldap_search(self, scope=ldap.SCOPE_SUBTREE, filterstr='(objectClass=*)'):
    results = []
    self.simple_bind_s(who=self.config["user"], cred=self.config["pass"])
    ldap_search = self.search(self.base_dn, scope, filterstr)
    for res_type, res_data, res_msgid, res_controls in self.allresults(ldap_search):
      for dn, entry in res_data:
        results.append(entry)
    return results

  def is_valid_user(self, user):
    is_valid_user_query = self.config["queries"]["user_is_valid"]
    query = is_valid_user_query.replace("USER", user)
    ldap_search = self.ldap_search(filterstr=query)
    if len(ldap_search) > 0:
      return True
    else:
      return False

  def is_active_user(self, user):
    is_active_user_query = self.config["queries"]["user_is_active"]
    query = is_active_user_query.replace("USER", user)
    ldap_search = self.ldap_search(filterstr=query)
    if len(ldap_search) > 0:
      return True
    else:
      return False

  def get_user_info(self, user):
    user_info_query = self.config["queries"]["user_info"]
    query = user_info_query.replace("USER", user)
    user_info = self.ldap_search(filterstr=query)
    return user_info[0]

  def sync_users(self):
    users = []
    all_users_query = self.config["queries"]["all_users"]
    ldap_search = self.ldap_search(filterstr=all_users_query)
    for result in ldap_search:
      if "uid" in result:
        users.append(result["uid"][0])
    return users


class LdapSyncThread(object):
  def __init__(self, t, hfunction):
    self.t=t
    self.hfunction = hfunction
    self.thread = Timer(self.t, self.handle_function)

  def handle_function(self):
    self.hFunction()
    self.thread = Timer(self.t, self.handle_function)
    self.thread.start()

  def start(self):
    self.thread.start()

  def cancel(self):
    self.thread.cancel()
