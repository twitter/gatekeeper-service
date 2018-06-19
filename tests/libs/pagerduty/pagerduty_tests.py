import json
from unittest import TestCase
import os

from pagerduty import PagerDutyApi

from mock import patch, MagicMock


CALL_PAGERDUTY_API = "pagerduty.HttpController.api_request"


class PagerDutyApiTests(TestCase):

  def read_resource_file(self, res_file):
    mock_results_dir = "tests/libs/pagerduty/mock_results"
    try:
      mock_resource_file = os.path.join(mock_results_dir, res_file)
      with open(mock_resource_file, "r") as fp:
        self.mock_resource = json.loads(fp.read())
        fp.close()
    except IOError:
      self.mock_resource = None

    return self.mock_resource

  @patch(CALL_PAGERDUTY_API)
  def test_delete_user_pass(self, mock_pagerduty_api):
    mock_pagerduty_api.return_value = ""
    pagerduty_admin = PagerDutyApi(use_proxy=False, config=MagicMock())
    delete_user = pagerduty_admin.delete_user(user_id="PP7WT8E")
    assert delete_user == ""
