import json

from google.controller import GoogleApiController
from helper_functions import HelperFunctions


class GoogleAdminApi(GoogleApiController):
  def __init__(self, oauth, config=None):
    self.oauth = oauth
    self.config = config
    self.service = self._get_service("admin", "directory_v1")

  def get_user_name(self, user_key):
    """
    Return a user's name object.
    :param user_key:
    :return: name object
    """
    try:
      r = json.loads(self.call_google_api(service=self.service,
                                          api_resource="users",
                                          api_method="get",
                                          response_field="name",
                                          userKey=user_key))
      return r
    except(ValueError, KeyError, TypeError):
      return None

  def is_suspended(self, user_key):
    """
    Check if user is suspended.
    :param user_key:
    :return: bool, True is user is suspended, False otherwise.
    """
    try:
      r = json.loads(self.call_google_api(service=self.service,
                                          api_resource="users",
                                          api_method="get",
                                          response_field="suspended",
                                          userKey=user_key))

      return r
    except(ValueError, KeyError, TypeError):
      return None

  def suspend(self, user_key):
    """
    Suspends a user.
    :param user_key: userKey
    :return: bool
    Note: When suspending a user, we expect the response to be True.
    """
    result = True
    try:
      r = json.loads(self.call_google_api(service=self.service,
                                          api_resource="users",
                                          api_method="update",
                                          response_field="suspended",
                                          userKey=user_key,
                                          body={"suspended": True}))
      if r is True:
        result = True
    except(ValueError, KeyError, TypeError):
      result = False
    return result

  def un_suspend(self, user_key):
    """
    Un-suspends a user.
    :param user_key: userKey
    :return: bool
    Note: When un-suspending a user, we expect the response to be False.
    """
    try:
      r = json.loads(self.call_google_api(service=self.service,
                                          api_resource="users",
                                          api_method="update",
                                          response_field="suspended",
                                          userKey=user_key,
                                          body={"suspended": False}))
      if r is False:
        return True
      else:
        return False
    except(ValueError, KeyError, TypeError):
      return False

  def delete_user(self, user_key):
    """
    Deletes a user.
    :param user_key: userKey
    :return: bool
    Note: When successful, this request returns an empty body.
    """
    r = self.call_google_api(service=self.service,
                             api_resource="users",
                             api_method="delete",
                             response_field=None,
                             userKey=user_key)
    if r == "":
      return True
    else:
      return False

  def reset_password(self, user_key):
    """
    Resets a user's password.
    :param user_key: userKey
    :return: bool
    Note: The password field is always returned empty.
    """
    result = True
    passwd = HelperFunctions().hash_passwd()
    try:
      r = json.loads(self.call_google_api(service=self.service,
                                          api_resource="users",
                                          api_method="update",
                                          response_field=None,
                                          userKey=user_key,
                                          body={"password": passwd,
                                                "hashFunction": "SHA-1"}))
      if "password" in r:
        if r["password"] == "":
          result = True
    except(ValueError, KeyError, TypeError):
      result = False
    return result

  def list_asps(self, user_key):
    """
    Lists a user's ASPs.
    :param user_key: userKey
    :return: list of ASP CodeIds
    """
    try:
      code_ids = []
      r = json.loads(self.call_google_api(service=self.service,
                                          api_resource="asps",
                                          api_method="list",
                                          response_field="items",
                                          userKey=user_key))
      if r is not None:
        for asp in r:
          code_ids.append(asp["codeId"])
      return code_ids
    except(ValueError, KeyError, TypeError):
      return False

  def delete_asp(self, user_key, code_id):
    """
    Deletes a user's ASP.
    :param user_key: userKey
    :param code_id: codeId
    :return: bool
    Note: When successful, this request returns an empty body.
    """
    try:
      r = json.loads(self.call_google_api(service=self.service,
                                          api_resource="asps",
                                          api_method="delete",
                                          response_field=None,
                                          userKey=user_key,
                                          codeId=code_id))
      if r == "":
        return True
      else:
        return False
    except(ValueError, KeyError, TypeError):
      return False

  def delete_asps(self, user_key):
    """
    Deletes all ASPs from a user account.
    :param user_key: userKey
    :return: dict of codeId,bool
    """
    try:
      results = {}
      code_ids = self.list_asps(user_key=user_key)
      if code_ids is not None:
        for code_id in code_ids:
          result = self.delete_asp(user_key=user_key, code_id=code_id)
          results[code_id] = result
          if result is False:
            print("Error deleting ASP codeId: %s" % code_id)
      return results
    except(ValueError, KeyError, TypeError):
      return False

  def list_tokens(self, user_key):
    """
    Lists a user's OAuth Tokens.
    :param user_key: userKey
    :return: list of OAuth Token clientIds
    """
    try:
      client_ids = []
      r = json.loads(self.call_google_api(service=self.service,
                                          api_resource="tokens",
                                          api_method="list",
                                          response_field="items",
                                          userKey=user_key))
      if r is not None:
        for token in r:
          client_ids.append(token["clientId"])
      return client_ids
    except(ValueError, KeyError, TypeError):
      return None

  def delete_token(self, user_key, client_id):
    """
    Deletes a user's OAuth Token.
    :param user_key: userKey
    :param client_id: clientId
    :return: bool
    Note: When successful, this request returns an empty body.
    """
    try:
      r = json.loads(self.call_google_api(service=self.service,
                                          api_resource="tokens",
                                          api_method="delete",
                                          response_field=None,
                                          userKey=user_key,
                                          clientId=client_id))
      if r == "":
        return True
      else:
        return False
    except(ValueError, KeyError, TypeError):
      return False

  def delete_tokens(self, user_key):
    """
    Deletes all OAuth Tokens from a user account.
    :param user_key: userKey
    :return: dict of clientId,bool
    """
    try:
      results = {}
      client_ids = self.list_tokens(user_key=user_key)
      if client_ids is not None:
        for client_id in client_ids:
          result = self.delete_token(user_key=user_key, client_id=client_id)
          results[client_id] = result
          if result is False:
            print("Error deleting OAuth Token clientId: %s" % client_id)
      return results
    except(ValueError, KeyError, TypeError):
      return False

  def list_backup_codes(self, user_key):
    """
    Lists a users backup codes.
    :param user_key: userKey
    :return: list
    Note: When successful, this request returns an empty body.
    """
    try:
      backup_codes = []
      r = json.loads(self.call_google_api(service=self.service,
                                          api_resource="verificationCodes",
                                          api_method="list",
                                          response_field="items",
                                          userKey=user_key))
      if r is not None:
        for code in r:
          backup_codes.append(code['verificationCode'])
        return backup_codes
    except(ValueError, KeyError, TypeError):
      return False

  def invalidate_backup_codes(self, user_key):
    """
    Invalidates a users backup codes.
    :param user_key: userKey
    :return: bool
    Note: When successful, this request returns an empty body.
    """
    if self.is_suspended(user_key):
      self.un_suspend(user_key)
    try:
      r = json.loads(self.call_google_api(service=self.service,
                                          api_resource="verificationCodes",
                                          api_method="invalidate",
                                          response_field=None,
                                          userKey=user_key))
      if r == "":
        return True
      else:
        return False
    except(ValueError, KeyError, TypeError):
      return False

  def generate_backup_codes(self, user_key):
    """
    Generates new user backup codes.
    :param user_key: userKey
    :return: bool
    Note: When successful, this request returns an empty body.
    """
    try:
      r = json.loads(self.call_google_api(service=self.service,
                                          api_resource="verificationCodes",
                                          api_method="generate",
                                          response_field=None,
                                          userKey=user_key))
      if r == "":
        return True
      else:
        return False
    except(ValueError, KeyError, TypeError):
      return False

  def org_unit_change(self, user_key):
    """
    Moves user to offboarded OrgUnit.
    :param user_key: userKey
    :param org_unit_path: orgUnitPath
    :return: bool
    Note: When successful, this request returns None.
    """
    org_unit_path = self.config["offboarded_ou"]
    try:
      r = json.loads(self.call_google_api(service=self.service,
                                          api_resource="users",
                                          api_method="update",
                                          response_field="primaryEmail",
                                          userKey=user_key,
                                          body={"orgUnitPath": org_unit_path}))
      if r == user_key:
        return True
      else:
        return False
    except(ValueError, KeyError, TypeError):
      return False

  def org_unit_reset(self, user_key):
    """
    Moves a user back to the default OrgUnit.
    :param user_key: userKey
    :return: bool
    Note: When successful, this request returns None.
    """
    try:
      r = json.loads(self.call_google_api(service=self.service,
        api_resource="users",
        api_method="update",
        response_field="primaryEmail",
        userKey=user_key,
        body={"orgUnitPath": "/"}))
      if r == user_key:
        return True
      else:
        return False
    except(ValueError, KeyError, TypeError):
      return False

  def group_member_list(self, group_key):
    """
    Lists members of a group.
    :param group_key: groupKey
    :return: list
    Note: Returns a list of group member email addresses.
    """
    try:
      group_members = []
      r = json.loads(self.call_google_api(service=self.service,
                                          api_resource="members",
                                          api_method="list",
                                          response_field="members",
                                          groupKey=group_key))
      for user in r:
        group_members.append(user['email'])
      return group_members
    except TypeError:
      return None

  def group_member_delete(self, group_key, user_key):
    """
    Removes member of a group.
    :param group_key: groupKey
    :param user_key: userKey
    :return: Bool
    Note: When successful, this request returns an empty body.
    """
    r = json.loads(self.call_google_api(service=self.service,
                                        api_resource="members",
                                        api_method="delete",
                                        response_field=None,
                                        groupKey=group_key,
                                        memberKey=user_key))
    if r == "":
      return True
    else:
      return False

  def two_step_status(self, user_key):
    """
    Returns the 2-step verification status of a user.
    :param user_key: userKey
    :return: Boolean
    Note: True if user is enrolled in 2-step verification
    """
    r = json.loads(self.call_google_api(service=self.service,
                                        api_resource="users",
                                        api_method="get",
                                        response_field="isEnrolledIn2Sv",
                                        userKey=user_key))
    return r

  def get_user_last_login(self, user_key):
    """
    Returns the last sign-in dates of a user.
    :param user_key: userKey
    :return: datetime object
    Note: Returns the late time a user logged in.
    """
    r = json.loads(self.call_google_api(service=self.service,
                                        api_resource="users",
                                        api_method="get",
                                        response_field="lastLoginTime",
                                        userKey=user_key))
    return r

  def get_user_alias(self, user_key):
    """
    Returns any alias associated with a user.
    :param user_key: user_key
    :return: alias object
    Note: Returns a list of aliases.
    """
    r = json.loads(self.call_google_api(service=self.service,
                                        api_resource="users",
                                        api_method="get",
                                        response_field="aliases",
                                        userKey=user_key))
    return r

  def add_user_alias(self, user_key, alias):
    """
    Adds an alias for a user.
    :param user_key: user_key
    :param alias: alias
    :return: Boolean
    Note: Returns if alias added successfully.
    """
    r = json.loads(self.call_google_api(service=self.service,
                                        api_resource="users.aliases",
                                        api_method="insert",
                                        response_field="alias",
                                        userKey=user_key,
                                        body={"alias": alias}))



    if r == alias:
      return True
    else:
      return False

  def delete_user_alias(self, user_key, alias):
    """
    Deletes an alias from a user.
    :param user_key: user_key
    :param alias: alias
    :return: Boolean
    Note: When successful, this request returns empty.
    """
    r = json.loads(self.call_google_api(service=self.service,
                                        api_resource="users.aliases",
                                        api_method="delete",
                                        response_field=None,
                                        userKey=user_key,
                                        alias=alias))
    if r == "":
      return True
    else:
      return False

  def create_user(self, user_key, last_name, first_name):
    """
    Creates a user account.
    :param user_key: user_key
    :param last_name: last_name
    :param first_name: first_name
    :return: user object
    Note: When successful this returns a user object.
    """
    passwd = HelperFunctions().hash_passwd()
    user_body = {
      "name": {
        "familyName": last_name,
        "givenName": first_name,
      },
      "password": passwd,
      "hashFunction": "SHA-1",
      "primaryEmail": user_key,
    }

    r = json.loads(self.call_google_api(service=self.service,
                                        api_resource="users",
                                        api_method="insert",
                                        response_field=None,
                                        body=user_body))
    return r

