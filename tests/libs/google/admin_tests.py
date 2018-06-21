import os
import json

from unittest import TestCase

from mock import MagicMock, patch
from google.admin import GoogleAdminApi

CALL_GOOGLE_API = "google.admin.GoogleApiController.call_google_api"


class SomeGoogleAdminApi(GoogleAdminApi):
  def __init__(self, oauth):
    self.config = MagicMock()
    self.oauth = oauth
    self.service = MagicMock()


class GoogleAdminApiTests(TestCase):
  def read_resource_file(self, res_file):
    mock_results_dir = "tests/libs/google/mock_results"
    try:
      mock_resource_file = os.path.join(mock_results_dir, res_file)
      with open(mock_resource_file, "r") as mock_resource_fp:
        self.mock_resource = json.loads(mock_resource_fp.read())
      mock_resource_fp.close()
    except IOError:
      self.mock_resource = None

    return self.mock_resource

  @patch(CALL_GOOGLE_API)
  def test_get_user_name(self, mock_google_api):
    mock_google_api.return_value = json.dumps(self.read_resource_file('get_user_name')["fullName"])
    google_admin = SomeGoogleAdminApi(oauth=MagicMock())
    get_user_name = google_admin.get_user_name("hkantas@testdomain.com")
    assert get_user_name == "Harry Kantas"

  @patch(CALL_GOOGLE_API)
  def test_is_suspended_pass(self, mock_google_api):
    mock_google_api.return_value = json.dumps(self.read_resource_file('user_resource')["suspended"])
    google_admin = SomeGoogleAdminApi(oauth=MagicMock())
    is_suspended = google_admin.is_suspended("someuser@somewhere.org")
    assert is_suspended is False

  @patch(CALL_GOOGLE_API)
  def test_is_suspended_fail(self, mock_google_api):
    mock_google_api.return_value = self.read_resource_file('user_resource_malformed')
    google_admin = SomeGoogleAdminApi(oauth=MagicMock())
    is_suspended = google_admin.is_suspended("someuser@somewhere.org")
    assert is_suspended is None

  @patch(CALL_GOOGLE_API)
  def test_suspend(self, mock_google_api):
    mock_google_api.return_value = json.dumps(self.read_resource_file('suspend')["suspended"])
    google_admin = SomeGoogleAdminApi(oauth=MagicMock())
    suspend = google_admin.suspend("someuser@somewhere.org")
    assert suspend is True

  @patch(CALL_GOOGLE_API)
  def test_un_suspend(self, mock_google_api):
    mock_google_api.return_value = json.dumps(self.read_resource_file('un_suspend')["suspended"])
    google_admin = SomeGoogleAdminApi(oauth=MagicMock())
    suspend = google_admin.suspend("someuser@somewhere.org")
    assert suspend is True

  @patch(CALL_GOOGLE_API)
  def test_delete_user_pass(self, mock_google_api):
    mock_google_api.return_value = ""
    google_admin = SomeGoogleAdminApi(oauth=MagicMock())
    delete_user = google_admin.delete_user("someuser@somewhere.org")
    assert delete_user is True

  @patch(CALL_GOOGLE_API)
  def test_delete_user_fail(self, mock_google_api):
    mock_google_api.return_value = json.dumps(self.read_resource_file('delete_user_resource_fail'))
    google_admin = SomeGoogleAdminApi(oauth=MagicMock())
    delete_user = google_admin.delete_user("someuser@somewhere.org")
    assert delete_user is False

  @patch(CALL_GOOGLE_API)
  def test_list_asps_pass(self, mock_google_api):
    mock_google_api.return_value = json.dumps(self.read_resource_file('asps_resource')["items"])
    google_admin = SomeGoogleAdminApi(oauth=MagicMock())
    list_asps = google_admin.list_asps("items")
    assert list_asps == [0, 2, 3]

  @patch(CALL_GOOGLE_API)
  def test_list_asps_fail(self, mock_google_api):
    mock_google_api.return_value = self.read_resource_file('asps_resource_malformed')["items"]
    google_admin = SomeGoogleAdminApi(oauth=MagicMock())
    list_asps = google_admin.list_asps("items")
    assert list_asps is False

  @patch(CALL_GOOGLE_API)
  def test_tokens_list_pass(self, mock_google_api):
    mock_google_api.return_value = json.dumps(self.read_resource_file('tokens_resource')["items"])
    google_admin = SomeGoogleAdminApi(oauth=MagicMock())
    list_tokens = google_admin.list_tokens("clientId")
    assert list_tokens == [("1011230515163-arsl01gv134b0sjidu62bkp3hub3nuj3."
                           "apps.googleusercontent.com")]

  @patch(CALL_GOOGLE_API)
  def test_tokens_list_fail(self, mock_google_api):
    mock_google_api.return_value = self.read_resource_file('tokens_resource_malformed')["items"]
    google_admin = SomeGoogleAdminApi(oauth=MagicMock())
    list_tokens = google_admin.list_tokens("clientId")
    assert list_tokens is None

  @patch(CALL_GOOGLE_API)
  def test_list_backup_codes_pass(self, mock_google_api):
    mock_google_api.return_value = json.dumps(self.read_resource_file
                                              ('verification_resource')["items"])
    google_admin = SomeGoogleAdminApi(oauth=MagicMock())
    list_backup_codes = google_admin.list_backup_codes("verificationCode")
    assert "26975385" in list_backup_codes

  @patch(CALL_GOOGLE_API)
  def test_list_backup_codes_fail(self, mock_google_api):
    mock_google_api.return_value = self.read_resource_file('verification_resource_fail')
    google_admin = SomeGoogleAdminApi(oauth=MagicMock())
    list_backup_codes = google_admin.list_backup_codes("verificationCode")
    assert list_backup_codes is False

  @patch(CALL_GOOGLE_API)
  def test_org_unit_change_pass(self, mock_google_api):
    mock_google_api.return_value = json.dumps(self.read_resource_file
                                              ('org_unit_change')["primaryEmail"])
    google_admin = SomeGoogleAdminApi(oauth=MagicMock())
    org_unit_change = google_admin.org_unit_change("stillings@testdomain.com")
    assert org_unit_change is True

  @patch(CALL_GOOGLE_API)
  def test_org_unit_change_fail(self, mock_google_api):
    mock_google_api.return_value = self.read_resource_file('org_unit_change')["primaryEmail"]
    google_admin = SomeGoogleAdminApi(oauth=MagicMock())
    org_unit_change = google_admin.org_unit_change("stillings@testdomain.com")
    assert org_unit_change is False

  @patch(CALL_GOOGLE_API)
  def test_group_members_list_pass(self, mock_google_api):
    mock_google_api.return_value = json.dumps(self.read_resource_file
                                              ('group_member_list')["members"])
    google_admin = SomeGoogleAdminApi(oauth=MagicMock())
    group_member_list = google_admin.group_member_list("group_key")
    assert group_member_list[1] == "phewson@testdomain.com"

  @patch(CALL_GOOGLE_API)
  def test_group_members_list_fail(self, mock_google_api):
    mock_google_api.return_value = json.dumps(self.read_resource_file('group_member_list_fail'))
    google_admin_api = SomeGoogleAdminApi(oauth=MagicMock())
    group_member_list = google_admin_api.group_member_list("group_key")
    assert group_member_list is None

  @patch(CALL_GOOGLE_API)
  def test_group_member_delete_pass(self, mock_google_api):
    mock_google_api.return_value = json.dumps(self.read_resource_file
                                              ('group_member_delete')["members"])
    google_admin_api = SomeGoogleAdminApi(oauth=MagicMock())
    group_member_delete = google_admin_api.group_member_delete("group_key", "user_key")
    assert group_member_delete is True

  @patch(CALL_GOOGLE_API)
  def test_group_member_delete_fail(self, mock_google_api):
    mock_google_api.return_value = json.dumps(self.read_resource_file('group_member_delete_fail'))
    google_admin_api = SomeGoogleAdminApi(oauth=MagicMock())
    group_member_delete = google_admin_api.group_member_delete("group_key", "user_key")
    assert group_member_delete is False
