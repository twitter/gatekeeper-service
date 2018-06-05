from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, TextAreaField, validators


"""
Note: field names must match the method names used by the various API client libraries.
Libraries are located under twexit/lib.
"""


class BaseForm(FlaskForm):
  def __iter__(self):
    token = self.csrf_token
    yield token

    field_names = {token.name}
    for cls in self.__class__.__bases__:
      for field in cls():
        field_name = field.name
        if field_name not in field_names:
          field_names.add(field_name)
          yield self[field_name]

    for field_name in self._fields:
      if field_name not in field_names:
        yield self[field_name]


class UserIdForm(BaseForm):
  USER_ID = StringField('LDAP user name', [validators.DataRequired(), validators.Length(min=2)])


class GoogleAdminApiForm(BaseForm):
  RESET_PASSWORD = BooleanField('Reset Google apps password')
  DELETE_ASPS = BooleanField('Purge application specific passwords')
  DELETE_TOKENS = BooleanField('Purge 3rd party access tokens')
  INVALIDATE_BACKUP_CODES = BooleanField('Invalidate backup codes')
  ORG_UNIT_CHANGE = BooleanField('Move to Offboarded OU')
  ORG_UNIT_RESET = BooleanField('Restore move to Offboarded OU')


class GoogleGmailApiForm(BaseForm):
  SET_OOO_MSG = BooleanField('Set Out Of Office message')
  OOO_MSG_TEXT = TextAreaField('Message text', [validators.Length(min=2)])
  DISABLE_IMAP = BooleanField('Disable IMAP email')
  DISABLE_POP = BooleanField('Disable POP email')


class GoogleCalendarApiForm(BaseForm):
  CHANGE_EVENTS_OWNERSHIP = BooleanField('Change events ownership')
  GCAL_NEW_OWNER = StringField('LDAP of new owner', [validators.Length(min=2)])
  REMOVE_FUTURE_EVENTS = BooleanField('Delete future dated events')


class PagerDutyApiForm(BaseForm):
  REMOVE_FROM_ONCALLS = BooleanField('Remove from OnCall rotas')


class DuoApiForm(BaseForm):
  REMOVE_FROM_DUO = BooleanField('Remove from DUO')


class GoogleApiForms(GoogleAdminApiForm, GoogleGmailApiForm, GoogleCalendarApiForm):
  pass


class OffboardForm(UserIdForm, GoogleApiForms, PagerDutyApiForm, DuoApiForm):
  pass


class LostAssetForm(UserIdForm, GoogleAdminApiForm, GoogleGmailApiForm):
  pass


class GoogleMailForwardingForm(BaseForm):
  SET_MAIL_FORWARDING = BooleanField('Set a mail forwarding address')


class GoogleDriveForm(BaseForm):
  FILE_SEARCH = StringField('File Search Query', [validators.Length(min=2)])
  NEW_OWNER = StringField('New files owner', [validators.DataRequired(), validators.Length(min=2)])


class FilesOwnershipTransferForm(UserIdForm, GoogleDriveForm):
  pass
