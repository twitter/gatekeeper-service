import json

from apiclient import discovery
from oauth2client.client import HttpAccessTokenRefreshError


class GoogleApiController(object):
  def __init__(self, oauth):
    self.oauth = oauth

  def _get_service(self, google_service, google_api):
    """
    Builds a connector to the admin service via the discovery api.
    :return:
      service, the service connector.
    """
    try:
      service = discovery.build(google_service, google_api, http=self.oauth)
    except (discovery.HttpError, HttpAccessTokenRefreshError) as e:
      print("Error building a service connector. %s" % e)
      service = None
    return service

  def call_google_api(self, service, api_resource, api_method, response_field, **kwargs):
    """
    Performs a call to Google's API Services.
    :args:
      api_resource, the Google Resource object to create.
      api_method, the method to perform.
    :return:
      resource, the resulting resource json object field.
    """
    try:
      api_resources = api_resource.split(".")
      google_resource = getattr(service, api_resources[0])()
      for res in api_resources[1:]:
        google_resource = getattr(google_resource, res)()
      resource_method = getattr(google_resource, api_method)(**kwargs)
      results = resource_method.execute()
      if response_field is not None:
        results = results.get(response_field)
    except discovery.HttpError:
      print("Error talking to Google API")
      results = None
    return json.dumps(results)
