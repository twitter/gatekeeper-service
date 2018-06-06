import json

from google.controller import GoogleApiController


class GoogleGmailApi(GoogleApiController):
  def __init__(self, oauth):
    self.oauth = oauth
    self.service = self._get_service("gmail", "v1")

  def set_ooo_msg(self, user_id, text):
    """
    Sets a vacation responder for the user.
    :param user_id: userId
    :return: bool
    """

    vacation_settings = {
      'enableAutoReply': True,
      'responseBodyHtml': text,
      'restrictToDomain': False,
    }
    try:
      r = json.loads(self.call_google_api(service=self.service,
                                          api_resource="users.settings",
                                          api_method="updateVacation",
                                          response_field="enableAutoReply",
                                          userId=user_id,
                                          body=vacation_settings))
      return r
    except(ValueError, KeyError, TypeError):
      return False

  def is_forwarding_address(self, user_id, fwd_email):
    """
    Checks whether an address is registered and verified for mail forwarding.
    :param user_id: userId
    :param email_address: emailAddress
    :return: bool
    """
    try:
      r = json.loads(self.call_google_api(service=self.service,
                                          api_resource="users.settings.forwardingAddresses",
                                          api_method="get",
                                          response_field="verificationStatus",
                                          userId=user_id,
                                          forwardingEmail=fwd_email))
      if r == "accepted":
        return True
      else:
        return False
    except(ValueError, KeyError, TypeError):
      return False

  def create_forwarding_address(self, user_id, fwd_email):
    """
    Creates mail forwarding for a user.
    :param user_id: userId
    :param fwd_email: emailAddress
    :return: bool
    """
    forwarding_settings = {
      'forwardingEmail': fwd_email,
      'verificationStatus': 'accepted'
    }
    try:
      r = json.loads(self.call_google_api(service=self.service,
                                          api_resource="users.settings.forwardingAddresses",
                                          api_method="create",
                                          response_field="verificationStatus",
                                          userId=user_id,
                                          body=forwarding_settings))
      if r == "accepted":
        return True
      else:
        return False
    except(ValueError, TypeError, KeyError):
      return False

  def set_mail_forwarding(self, user_id, fwd_email):
    """
    Enables mail forwarding for the user.
    :param user_id: userId
    :param fwd_email: emailAddress
    :return: bool
    """

    if not self.is_forwarding_address(user_id=user_id, fwd_email=fwd_email):
      self.create_forwarding_address(user_id=user_id, fwd_email=fwd_email)

    forwarding_settings = {
      'emailAddress': fwd_email,
      'enabled': True,
      'disposition': 'leaveInInbox',
    }

    try:
      r = json.loads(self.call_google_api(service=self.service,
                                          api_resource="users.settings",
                                          api_method="updateAutoForwarding",
                                          response_field="enabled",
                                          userId=user_id,
                                          body=forwarding_settings))
      return r
    except(ValueError, TypeError, KeyError):
      return False

  def disable_pop(self, user_id):
    """
    Disables POP for the user.
    :param user_id:
    :return: bool
    Note: If accessWindow=disabled, then POP is disabled.
    """
    pop_setting = {
      'accessWindow': 'disabled'
    }

    try:
      r = json.loads(self.call_google_api(service=self.service,
                                          api_resource="users.settings",
                                          api_method="updatePop",
                                          response_field="accessWindow",
                                          userId=user_id,
                                          body=pop_setting))
      if r == "disabled":
        return True
      else:
        return False
    except(ValueError, KeyError, TypeError):
      return False

  def disable_imap(self, user_id):
    """
    Disables IMAP for the user.
    :param user_id:
    :return: bool
    Note: If enabled=False, then IMAP is disabled.
    """
    imap_setting = {
      'enabled': 'False'
    }

    try:
      r = json.loads(self.call_google_api(service=self.service,
                                          api_resource="users.settings",
                                          api_method="updateImap",
                                          response_field="enabled",
                                          userId=user_id,
                                          body=imap_setting))
      if r is False:
        return True
      else:
        return False
    except(ValueError, KeyError, TypeError):
      return False
