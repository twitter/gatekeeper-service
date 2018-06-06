import os
import json

from unittest import TestCase

from mock import MagicMock, patch
from google.controller import GoogleApiController

CALL_GOOGLE_API = "google.controller.GoogleApiController.call_google_api"


class SomeGoogleApiController(GoogleApiController):
  def __init__(self, oauth):
    self.oauth = oauth
    self.service = MagicMock()


class GoogleApiControllerTests(TestCase):

  def setUp(self):
    mock_results_dir = "tests/libs/google/mock_results"
    mock_resource_file = os.path.join(mock_results_dir, "user_resource")
    try:
      with open(mock_resource_file, "r") as mock_resource_fp:
        self.mock_resource = json.loads(mock_resource_fp.read())
      mock_resource_fp.close()
    except IOError:
      self.mock_resource = None

  @patch(CALL_GOOGLE_API)
  def test_is_suspended_pass(self, mock_google_api):
    mock_google_api.return_value = json.dumps(self.mock_resource["suspended"])
    google_controller = SomeGoogleApiController(oauth=MagicMock())
    is_suspended = google_controller.call_google_api(service=None,
                                                     api_resource="users",
                                                     api_method="get",
                                                     response_field="suspended")
    assert json.loads(is_suspended) is False
