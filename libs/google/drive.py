import json

from google.controller import GoogleApiController


class GoogleDriveApi(GoogleApiController):
  def __init__(self, oauth):
    self.oauth = oauth
    self.service = self._get_service("drive", "v3")

  def get_files_list(self, owner):
    """
    Retrieves a user's drive files
    :return: list of files owned by the user.
    """
    files_list = []
    try:
      r = json.loads(self.call_google_api(service=self.service,
                                          q=owner,
                                          api_resource="files",
                                          api_method="list",
                                          response_field=None,
                                          corpus="user",
                                          spaces="drive"))
      files_list.extend(r["files"])

      if "nextPageToken" in r:
        next_page_token = r["nextPageToken"]
        while next_page_token is not None:
          r = json.loads(self.call_google_api(service=self.service,
                                              q=owner,
                                              api_resource="files",
                                              api_method="list",
                                              response_field=None,
                                              corpus="user",
                                              spaces="drive",
                                              pageToken=next_page_token))
          files_list.extend(r["files"])
          if "nextPageToken" in r:
            next_page_token = r["nextPageToken"]
          else:
            next_page_token = None

      return files_list
    except(ValueError, KeyError, TypeError):
      return None

  def search_files_list(self, owner="'me' in owners", drive_query=""):
    """
    Searches users drives files
    :param drive_query: q
    :param owner: q
    :return: list of files with name containing the searched term.
    """
    files_list = []
    try:
      file_search = "%s and name contains '%s'" % (owner, drive_query)
      r = json.loads(self.call_google_api(service=self.service,
                                          q=file_search,
                                          api_resource="files",
                                          api_method="list",
                                          response_field=None,
                                          corpus="user",
                                          spaces="drive"))
      files_list.extend(r["files"])

      if "nextPageToken" in r:
        next_page_token = r["nextPageToken"]
        while next_page_token is not None:
          r = json.loads(self.call_google_api(service=self.service,
                                              q=file_search,
                                              api_resource="files",
                                              api_method="list",
                                              response_field=None,
                                              corpus="user",
                                              spaces="drive",
                                              pageToken=next_page_token))
          files_list.extend(r["files"])
          if "nextPageToken" in r:
            next_page_token = r["nextPageToken"]
          else:
            next_page_token = None

      return files_list
    except(ValueError, KeyError, TypeError):
      return None

  def get_file_info(self, file_id):
    """
    Lists a file's metadata.
    :param file_id: fileId
    :return: files resource
    """
    try:
      r = json.loads(self.call_google_api(service=self.service,
                                          api_resource="files",
                                          api_method="get",
                                          fields="owners",
                                          fileId=file_id,
                                          response_field=None))
      return r
    except(ValueError, KeyError, TypeError):
      return None

  def transfer_file_owner(self, file_id, user_email):
    """
    Assigned new owner for the file
    :param file_id: fileId
    :param user_email: permissionId
    :return: bool
    """
    permissions_settings = {
      "kind": "drive#permission",
      "role": "owner",
      "type": "user",
      "emailAddress": user_email
    }
    try:
      r = json.loads(self.call_google_api(service=self.service,
                                          api_resource="permissions",
                                          api_method="create",
                                          response_field="role",
                                          fileId=file_id,
                                          transferOwnership=True,
                                          body=permissions_settings))

      if r == "owner":
        return True
      else:
        return False
    except(ValueError, KeyError, TypeError):
      return False
