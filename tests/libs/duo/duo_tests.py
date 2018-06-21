import os
import json
from unittest import TestCase

from duo import DuoAdminApi

from mock import patch


CALL_DUO_API = "duo.duo_client.Admin"


class SomeDuoAdminApi(DuoAdminApi):
  def __init__(self, admin_api):
    self.admin_api = admin_api


class DuoAdminApiTests(TestCase):

  def read_resource_file(self, res_file):
    mock_results_dir = "tests/libs/duo/mock_results"
    try:
      mock_resource_file = os.path.join(mock_results_dir, res_file)
      with open(mock_resource_file, "r") as fp:
        self.mock_resource = fp.read()
        fp.close()
    except IOError:
      self.mock_resource = None

    return self.mock_resource

  @patch(CALL_DUO_API)
  def test_list_users_pass(self, mock_duo_api):
    mock_duo_api.get_users.return_value = json.loads(self.read_resource_file('list_users_resource'))
    duo_api = SomeDuoAdminApi(admin_api=mock_duo_api)
    list_users = duo_api.list_users()
    assert list_users[0]["username"] == "mat"

  @patch(CALL_DUO_API)
  def test_list_users_fail(self, mock_duo_api):
    mock_duo_api.get_users.return_value = json.loads(
      self.read_resource_file('list_users_resource_fail'))
    duo_api = SomeDuoAdminApi(admin_api=mock_duo_api)
    list_users = duo_api.list_users()
    assert list_users == []

  @patch(CALL_DUO_API)
  def test_get_user_pass(self, mock_duo_api):
    mock_duo_api.get_users_by_name.return_value = json.loads(
      self.read_resource_file('get_user_resource'))
    duo_api = SomeDuoAdminApi(admin_api=mock_duo_api)
    get_user = duo_api.get_user("mat")
    assert get_user[0]["realname"] == "Mat Clinton"

  @patch(CALL_DUO_API)
  def test_get_user_fail(self, mock_duo_api):
    mock_duo_api.get_users_by_name.return_value = json.loads(
      self.read_resource_file('get_user_resource_fail'))
    duo_api = SomeDuoAdminApi(admin_api=mock_duo_api)
    get_user = duo_api.get_user("mat")
    assert get_user == []

  @patch(CALL_DUO_API)
  def test_delete_user_pass(self, mock_duo_api):
    mock_duo_api.delete_user.return_value = ""
    duo_api = SomeDuoAdminApi(admin_api=mock_duo_api)
    delete_user = duo_api.delete_user("DUVVVVVVVVVVV")
    assert delete_user is True

  @patch(CALL_DUO_API)
  def test_delete_user_fail(self, mock_duo_api):
    mock_duo_api.delete_user.return_value = json.loads(
      self.read_resource_file('delete_user_resource_fail'))
    duo_api = SomeDuoAdminApi(admin_api=mock_duo_api)
    delete_user = duo_api.delete_user("DUVVVVVVVVVVV")
    assert delete_user is False
