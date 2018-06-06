import os
import json

from unittest import TestCase

from mock import MagicMock, patch
from google.calendar import GoogleCalendarApi


CALL_GOOGLE_API = "google.calendar.GoogleApiController.call_google_api"


class SomeGoogleCalendarApi(GoogleCalendarApi):
  def __init__(self, oauth):
    self.oauth = oauth
    self.service = MagicMock()


class GoogleCalendarApiTests(TestCase):

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
  def test_get_calendar_id_pass(self, mock_google_api):
    mock_google_api.return_value = json.dumps(self.read_resource_file('calendar_id_resource')["id"])
    google_calendar = SomeGoogleCalendarApi(oauth=MagicMock())
    get_calendar_id = google_calendar.get_calendar_id()
    assert get_calendar_id == "hkantas@testdomain.com"

  @patch(CALL_GOOGLE_API)
  def test_get_calendar_id_fail(self, mock_google_api):
    mock_google_api.return_value = self.read_resource_file('calendar_id_resource_malformed')
    google_calendar = SomeGoogleCalendarApi(oauth=MagicMock())
    get_calendar_id = google_calendar.get_calendar_id()
    assert get_calendar_id is None

  @patch(CALL_GOOGLE_API)
  def test_list_events(self, mock_google_api):
    mock_google_api.return_value = json.dumps(self.read_resource_file
                                              ('list_events_resource')["items"])
    google_calendar = SomeGoogleCalendarApi(oauth=MagicMock())
    list_events = google_calendar.list_events("someuser@somewhere.org")
    assert list_events[0] == "ksk6hnh8lbe0qdn02tc1vsp7qk"

  @patch(CALL_GOOGLE_API)
  def test_move_event(self, mock_google_api):
    mock_google_api.return_value = json.dumps(self.read_resource_file
                                              ('move_event_resource')["id"])
    google_calendar = SomeGoogleCalendarApi(oauth=MagicMock())
    move_event = google_calendar.move_event("ltk5efr9set0qaogfnpapgvcec",
                                            "stillings@testdomain.com")
    assert move_event is True

  @patch(CALL_GOOGLE_API)
  def test_move_calendar_ownership(self, mock_google_api):
    mock_google_api.return_value = json.dumps(self.read_resource_file
                                              ('move_calendar_resource')["role"])
    google_calendar = SomeGoogleCalendarApi(oauth=MagicMock())
    move_calendar = google_calendar.move_calendar_ownership("mat@testdomain.com")
    assert move_calendar == "owner"

  @patch(CALL_GOOGLE_API)
  def test_decline_event(self, mock_google_api):
    mock_google_api.return_value = json.dumps(self.read_resource_file
                                              ('decline_event_resource')["attendees"])
    google_calendar = SomeGoogleCalendarApi(oauth=MagicMock())
    decline_event = google_calendar.decline_event("fuccsmq6ipqmpeeb93e6bdvtc0",
                                                  "stillings@testdomain.com")
    assert decline_event[0]["responseStatus"] == "declined"

  @patch(CALL_GOOGLE_API)
  def test_get_event_rule(self, mock_google_api):
    mock_google_api.return_value = json.dumps(self.read_resource_file
                                              ('event_rule_resource')["recurrence"])
    google_calendar = SomeGoogleCalendarApi(oauth=MagicMock())
    get_event_rule = google_calendar.get_event_rule("event_id")
    assert get_event_rule == ["RRULE:FREQ=WEEKLY;BYDAY=MO"]

  @patch(CALL_GOOGLE_API)
  def test_cancel_recurrence(self, mock_google_api):
    mock_google_api.return_value = json.dumps(self.read_resource_file
                                              ('cancel_recurrence_resource')["id"])
    google_calendar = SomeGoogleCalendarApi(oauth=MagicMock())
    cancel_recurrence = google_calendar.cancel_recurrence("event_id", "new_event_rule")
    assert cancel_recurrence == "e2i9ln9qjl3eo9ejgb3484bh78"
