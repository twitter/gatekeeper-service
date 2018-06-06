import os
import json

from unittest import TestCase

from mock import MagicMock, patch
from google.gmail import GoogleGmailApi

CALL_GOOGLE_API = "google.gmail.GoogleApiController.call_google_api"


class SomeGoogleGmailApi(GoogleGmailApi):
  def __init__(self, oauth):
    self.oauth = oauth
    self.service = MagicMock()


class GoogleGmailApiTests(TestCase):

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
  def test_set_ooo_msg_pass(self, mock_google_api):
    mock_google_api.return_value = json.dumps(self.read_resource_file
                                              ('ooo_resource')["enableAutoReply"])
    google_gmail = SomeGoogleGmailApi(oauth=MagicMock())
    set_ooo_msg = google_gmail.set_ooo_msg("someuser@somewhere.org", "text")
    assert set_ooo_msg is True

  @patch(CALL_GOOGLE_API)
  def test_set_ooo_msg_fail(self, mock_google_api):
    mock_google_api.return_value = self.read_resource_file('ooo_resource_malformed')
    google_gmail = SomeGoogleGmailApi(oauth=MagicMock())
    set_ooo_msg = google_gmail.set_ooo_msg("someuser@somewhere.org", "text")
    assert set_ooo_msg is False

  @patch(CALL_GOOGLE_API)
  def test_forwarding_address_enabled_pass(self, mock_google_api):
    mock_google_api.return_value = json.dumps(self.read_resource_file
                                              ('forwarding_resource')["verificationStatus"])
    google_gmail = SomeGoogleGmailApi(oauth=MagicMock())
    is_forwarding_address = google_gmail.is_forwarding_address("someuser@somewhere.org",
                                                               "someuser@gtest.twiter.com")
    assert is_forwarding_address is True

  @patch(CALL_GOOGLE_API)
  def test_forwarding_address_enabled_fail(self, mock_google_api):
    mock_google_api.return_value = self.read_resource_file('forwarding_resource')
    google_gmail = SomeGoogleGmailApi(oauth=MagicMock())
    is_forwarding_address = google_gmail.is_forwarding_address("someuser@somewhere.org",
                                                               "someuser@somewhere.org")
    assert is_forwarding_address is False

  @patch(CALL_GOOGLE_API)
  def test_create_forwarding_address(self, mock_google_api):
    mock_google_api.return_value = json.dumps(self.read_resource_file
                                              ('forwarding_resource')["verificationStatus"])
    google_gmail = SomeGoogleGmailApi(oauth=MagicMock())
    create_forwarding_address = google_gmail.create_forwarding_address("someuser@somewhere.org",
                                                                       "someuser@somewhere.org")
    assert create_forwarding_address is True

  @patch(CALL_GOOGLE_API)
  def test_disable_pop_pass(self, mock_google_api):
    mock_google_api.return_value = json.dumps(self.read_resource_file
                                              ('pop_resource')["accessWindow"])
    google_gmail = SomeGoogleGmailApi(oauth=MagicMock())
    disable_pop = google_gmail.disable_pop("someuser@somewhere.org")
    assert disable_pop is True

  @patch(CALL_GOOGLE_API)
  def test_disable_pop_fail(self, mock_google_api):
    mock_google_api.return_value = self.read_resource_file('pop_resource_malformed')
    google_gmail = SomeGoogleGmailApi(oauth=MagicMock())
    disable_pop = google_gmail.disable_pop("someuser@somewhere.org")
    assert disable_pop is False

  @patch(CALL_GOOGLE_API)
  def test_disable_imap_pass(self, mock_google_api):
    mock_google_api.return_value = json.dumps(self.read_resource_file
                                              ('imap_resource')["enabled"])
    google_gmail = SomeGoogleGmailApi(oauth=MagicMock())
    disable_imap = google_gmail.disable_imap("someuser@somewhere.org")
    assert disable_imap is True

  @patch(CALL_GOOGLE_API)
  def test_disable_imap_fail(self, mock_google_api):
    mock_google_api.return_value = self.read_resource_file('imap_resource_malformed')
    google_gmail = SomeGoogleGmailApi(oauth=MagicMock())
    disable_imap = google_gmail.disable_imap("someuser@somewhere.org")
    assert disable_imap is False
