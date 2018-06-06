import json

from google.controller import GoogleApiController
from helper_functions import HelperFunctions


class GoogleCalendarApi(GoogleApiController):
  def __init__(self, oauth):
    self.oauth = oauth
    self.service = self._get_service("calendar", "v3")

  def get_calendar_id(self):
    """
    Gets the Calendar ID for a user.
    :return: str(calendar_id)
    """
    try:
      r = json.loads(self.call_google_api(service=self.service,
                                          api_resource="calendars",
                                          api_method="get",
                                          response_field="id",
                                          calendarId="primary"))
      return r
    except(ValueError, KeyError, TypeError):
      return None

  def list_events(self, user_email, role="organizer"):
    """
    Lists the future dated events of a user.
    :param user_email: user_email
    :param role: organizer: attendee: owned_single_event
    :return: List of event ids.
    """
    now = HelperFunctions().date_now()

    events = []
    r = json.loads(self.call_google_api(service=self.service,
                                        api_resource="events",
                                        api_method="list",
                                        response_field="items",
                                        singleEvents=True,
                                        timeMin=now,
                                        orderBy="startTime",
                                        calendarId="primary"))

    if r is not None:

      if role == "organizer":
        for event in r:
          if (("organizer" in event) and
              (("self" in event["organizer"] and event["organizer"]["self"]) or
                (event["organizer"]["email"] == user_email))):
            if ("recurringEventId" in event):
              events.append(event["recurringEventId"])
            else:
              events.append(event["id"])

      elif role == "attendee":
        for event in r:
          if (("organizer" in event) and
              (("self" not in event["organizer"]) or
                (event["organizer"]["email"] != user_email))):
            if ("recurringEventId" in event):
              events.append(event["recurringEventId"])
            else:
              events.append(event["id"])

      elif role == "owned_single_event":
        for event in r:
          if (("organizer" in event) and
              (("self" in event["organizer"] and event["organizer"]["self"]) or
                (event["organizer"]["email"] == user_email))):
            if ("recurringEventId" not in event):
              events.append(event["id"])

      return list(set(events))

  def move_calendar_ownership(self, owner_calendar_id):
    acl = {
        "kind": "calendar#aclRule",
        "scope": {
            "type": "user",
            "value": owner_calendar_id
        },
        "role": "owner"
    }
    try:
      r = json.loads(self.call_google_api(service=self.service,
                                          api_resource="acl",
                                          api_method="insert",
                                          response_field=None,
                                          calendarId="primary",
                                          body=acl))
      return r
    except(ValueError, KeyError, TypeError):
      return None

  def move_event(self, event_id, destination_calendar_id):
    """
    Change calendar event owner.
    :param event_id: eventId
    :param destination_calendar_id: destination
    :return: bool
    """
    try:
      r = json.loads(self.call_google_api(service=self.service,
                                          api_resource="events",
                                          api_method="move",
                                          response_field="id",
                                          calendarId="primary",
                                          eventId=event_id,
                                          destination=destination_calendar_id))

      if r == event_id:
        return True
      else:
        return False
    except(ValueError, KeyError, TypeError):
      return None

  def delete_event(self, event_id):
    """
    Remove user from a calendar event.
    :param event_id: eventId
    :return: empty response when successful
    """
    try:
      r = json.loads(self.call_google_api(service=self.service,
                                          api_resource="events",
                                          api_method="delete",
                                          response_field=None,
                                          calendarId="primary",
                                          eventId=event_id,
                                          sendNotifications=False))
      if r is None:
        return True
      else:
        return False
    except(ValueError, KeyError, TypeError):
      return False

  def remove_events_attendance(self, user_email):
    """
    Deletes events a user owns from their calendar.
    :param user_email: user_email
    :return: list of event_ids removed.
    """
    events = self.list_events(user_email=user_email, role="owned_single_event")
    events_removed = []
    if events:
      for event in events:
        res = self.delete_event(event_id=event)
        if res:
          events_removed.append(event)
    return events_removed

  def decline_event(self, event_id, user_email):
    """
    Declines event.
    :param event_id: eventId
    :param user_email: user_email
    :return: event details
    """

    patch_body = {"attendees": [{"responseStatus": "declined", "email": user_email}]}
    try:
      r = json.loads(self.call_google_api(service=self.service,
                                          api_resource="events",
                                          api_method="patch",
                                          response_field="attendees",
                                          calendarId="primary",
                                          eventId=event_id,
                                          sendNotifications=False,
                                          body=patch_body))
      return r
    except(ValueError, KeyError, TypeError):
      return None

  def decline_events_attendance(self, user_email):
    """
    Declines all events from a user's calendar.
    :param user_email: userEmail
    :return: list of event_ids removed
    """
    events = self.list_events(user_email=user_email, role="attendee")
    events_declined = []
    if events:
      for event in events:
        res = self.decline_event(event_id=event, user_email=user_email)
        if res:
          events_declined.append(event)
    return events_declined

  def get_event_rule(self, event_id):
    """
    Gets the recurrence rrule value for an event.
    :param event_id: eventId
    :return: Recurrence rule as a list
    """
    try:
      r = json.loads(self.call_google_api(service=self.service,
                                          api_resource="events",
                                          api_method="get",
                                          response_field="recurrence",
                                          calendarId="primary",
                                          eventId=event_id))

      return r
    except(ValueError, KeyError, TypeError):
      return None

  def cancel_recurrence(self, event_id, new_event_rule):
    """
    Updates event recurrence rule to cancel future instances.
    :param event_id: eventId
    :param new_event_rule: body
    :return: list of canceled event ids.
    """

    patch_body = {
        "recurrence": new_event_rule
    }
    try:
      r = json.loads(self.call_google_api(service=self.service,
                                          api_resource="events",
                                          api_method="patch",
                                          response_field="id",
                                          calendarId="primary",
                                          eventId=event_id,
                                          sendNotifications=False,
                                          body=patch_body))
      return r
    except(ValueError, KeyError, TypeError):
      return None

  def remove_recurring_instances(self, user_email):
    """
    Cancels future event instances from a users calendar.
    :param user_email: user_email
    :return: list of canceled event ids.
    """
    updated_events = []
    recurring_events_list = self.list_events(user_email)
    if recurring_events_list:
      for event in recurring_events_list:
        event_rule = self.get_event_rule(event)
        if event_rule:
          new_event_rule = HelperFunctions.updated_event_rule(event_rule)
          updated_event = self.cancel_recurrence(event, new_event_rule)
          updated_events.append(updated_event)
      return updated_events
    else:
      return None

  def remove_future_events(self, user_email):
    """
    Removes attendance from future events, and cancels recurring events.
    :param self:
    :param user_email:
    :return: set of cancelled event ids.
    """
    cancelled_events = []
    cancelled_events.append(self.remove_events_attendance(user_email))
    cancelled_events.append(self.remove_recurring_instances(user_email))
    cancelled_events.append(self.decline_events_attendance(user_email))

    return cancelled_events
