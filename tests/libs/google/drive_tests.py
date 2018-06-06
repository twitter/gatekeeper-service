import os
import json

from unittest import TestCase

from mock import MagicMock, patch
from google.drive import GoogleDriveApi


CALL_GOOGLE_API = "google.drive.GoogleApiController.call_google_api"


class SomeGoogleDriveApi(GoogleDriveApi):
  def __init__(self, oauth):
    self.oauth = oauth
    self.service = MagicMock()


class GoogleDriveApiTests(TestCase):

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
  def test_get_files_list_pass(self, mock_google_api):
    file_ids = []
    mock_google_api.return_value = json.dumps(self.read_resource_file
                                              ('drive_list_resource'))
    google_drive = SomeGoogleDriveApi(oauth=MagicMock())
    get_files_list = google_drive.get_files_list("someuser@somehwere.org")
    for file_id in get_files_list:
      file_ids.append(file_id['id'])
    assert "0B3uO8LigBWypc3RhcnRlcl9maWxlX2Rhc2hlclYw" in file_ids

  @patch(CALL_GOOGLE_API)
  def test_get_files_list_fail(self, mock_google_api):
    mock_google_api.return_value = self.read_resource_file('drive_list_resource_malformed')
    google_drive = SomeGoogleDriveApi(oauth=MagicMock())
    get_files_list = google_drive.get_files_list("someuser@somehwere.org")
    assert get_files_list is None

  @patch(CALL_GOOGLE_API)
  def test_get_file_info_pass(self, mock_google_api):
    mock_google_api.return_value = json.dumps(self.read_resource_file('file_info_resource')["id"])
    google_drive = SomeGoogleDriveApi(oauth=MagicMock())
    get_file_info = google_drive.get_file_info("file_id")
    assert get_file_info == "0B-NxYpteIrCmZ2lIU3lheHA1dkE"

  @patch(CALL_GOOGLE_API)
  def test_get_file_info_fail(self, mock_google_api):
    mock_google_api.return_value = self.read_resource_file('file_info_resource_malformed')["id"]
    google_drive = SomeGoogleDriveApi(oauth=MagicMock())
    get_file_info = google_drive.get_file_info("file_id")
    assert get_file_info is None

  @patch(CALL_GOOGLE_API)
  def test_drive_transfer_file_owner_pass(self, mock_google_api):
    mock_google_api.return_value = json.dumps(self.read_resource_file
                                              ('drive_transfer_file_owner_pass')["role"])
    google_drive = SomeGoogleDriveApi(oauth=MagicMock())
    transfer_file_owner = google_drive.transfer_file_owner("file_id", "user_email")
    assert transfer_file_owner is True

  @patch(CALL_GOOGLE_API)
  def test_drive_transfer_file_owner_fail(self, mock_google_api):
    mock_google_api.return_value = json.dumps(self.read_resource_file
                                              ('drive_transfer_file_owner_fail'))
    google_drive = SomeGoogleDriveApi(oauth=MagicMock())
    transfer_file_owner = google_drive.transfer_file_owner("file_id", "user_email")
    assert transfer_file_owner is False
