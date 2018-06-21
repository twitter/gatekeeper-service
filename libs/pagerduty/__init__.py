import json

from http_controller import HttpController


class PagerDutyApi(HttpController):
  def __init__(self, config=None, **kwargs):
    self.config = config
    self.base_url = self.config["base_url"]
    self.api_key = self.config["api_key"]
    self.HEADERS = {"Authorization": "Token token={0}".format(self.api_key),
                    "Accept": "application/vnd.pagerduty+json;version=2",
                    "Content-type": "application/json"}
    super(PagerDutyApi, self).__init__(base_url=self.base_url, **kwargs)

  def find_user_id(self, user_email):
    """
    Returns a user, matching the given email.
    :param user_email: user email
    :return: user object
    """
    user_id = None
    params = {"query": user_email}
    try:
      list_users = self.api_request(method="get",
                                    endpoint="users",
                                    params=params,
                                    headers=self.HEADERS)
      if "users" in list_users and len(list_users["users"]) > 0:
        for user in list_users["users"]:
          if user["email"] == user_email:
            user_id = user["id"]
    except ValueError as e:
      print(e)

    return user_id

  def get_schedule_by_id(self, schedule_id):
    """
    retrieves a schedule by its ID.
    :param schedule_id
    :return: schedule object
    """
    r = self.api_request(method="get",
                         endpoint="schedules/{id}".format(id=schedule_id),
                         headers=self.HEADERS)
    return r

  def get_escalation_policy_by_id(self, policy_id):
    """
    retrieves an escalation policy by its ID.
    :param policy_id
    :return: escalation policy object
    """
    r = self.api_request(method="get",
                         endpoint="escalation_policies/{id}".format(id=policy_id),
                         headers=self.HEADERS)
    return r

  def get_service_by_id(self, service_id):
    """
    retrieves a service by its ID.
    :param service_id
    :return: service object
    """
    params = {"include[]": "escalation_policies"}
    r = self.api_request(method="get",
                         endpoint="services/{id}".format(id=service_id),
                         params=params,
                         headers=self.HEADERS)
    return r

  def update_schedule_by_id(self, schedule_id, schedule):
    """
    Updates a schedule by ID.
    :param schedule_id: schedule ID
    :param schedule: schedule object
    :return: bool
    """
    updated = True
    r = self.api_request(method="put",
                         endpoint="schedules/{id}".format(id=schedule_id),
                         data=json.dumps(schedule),
                         headers=self.HEADERS)
    if "error" in r:
      updated = False
    return updated

  def update_escalation_policy_by_id(self, policy_id, policy):
    """
    Updates an escalation policy by ID.
    :param policy_id: policy ID
    :param policy: escalation_policy object
    :return: bool
    """
    updated = True
    r = self.api_request(method="put",
                         endpoint="escalation_policies/{id}".format(id=policy_id),
                         data=json.dumps(policy),
                         headers=self.HEADERS)
    if "error" in r:
      updated = False

    return updated

  def update_service_by_id(self, service_id, service):
    """
    Updates a service by ID.
    :param service_id: service ID
    :param service: service object
    :return: bool
    """
    updated = True
    r = self.api_request(method="put",
                         endpoint="services/{id}".format(id=service_id),
                         data=json.dumps(service),
                         headers=self.HEADERS)
    if "error" in r:
      updated = False

    return updated

  def delete_escalation_policy_by_id(self, policy_id):
    """
    Deletes an escalation policy by ID.
    :param policy_id: policy ID
    :return: bool
    """
    deleted = False
    r = self.api_request(method="delete",
                         endpoint="escalation_policies/{id}".format(id=policy_id),
                         response_type="text",
                         headers=self.HEADERS)
    try:
      response = json.loads(r)
      if "error" in response:
        deleted = False
    except json.JSONDecoderError:
      if r == "":
        deleted = True
    return deleted

  def remove_user_from_schedule(self, schedule_id, user_id):
    """
    remove user from a schedule.
    :param schedule_id: schedule_id
    :param user_id: user_id
    :return: bool
    """
    schedule = self.get_schedule_by_id(schedule_id=schedule_id)

    for layer in schedule["schedule"]["schedule_layers"]:
      for user in layer["users"]:
        if user["user"]["id"] == user_id:
          user_idx = layer["users"].index(user)
          layer["users"].pop(user_idx)
          if len(layer["users"]) == 0:
            layer["users"].append(schedule["schedule"]["users"][0])
    removed = self.update_schedule_by_id(schedule_id=schedule_id, schedule=schedule)

    return removed

  def remove_user_from_escalation_policy(self, policy_id, user_id, delete_empty=False):
    """
    remove user from an escalation policy.
    :param policy_id: policy_id
    :param user_id: user_id
    :param delete_empty: whether to delete an escalation policy with no targets
    :return: bool
    """
    removed = False
    policy = self.get_escalation_policy_by_id(policy_id=policy_id)

    if len(policy["escalation_policy"]["escalation_rules"]) == 1:
      rule = policy["escalation_policy"]["escalation_rules"][0]
      if len(rule["targets"]) > 1:
        for target in rule["targets"]:
          if target["id"] == user_id:
            target_idx = rule["targets"].index(target)
            rule["targets"].pop(target_idx)
            removed = self.update_escalation_policy_by_id(policy_id=policy_id, policy=policy)
      elif delete_empty is True:
        for service in policy["escalation_policy"]["services"]:
          self.delete_service(service_id=service["id"])
        self.get_escalation_policy_by_id(policy_id=policy_id)
        removed = self.delete_escalation_policy_by_id(policy_id=policy_id)

    return removed

  def delete_service(self, service_id):
    """
    Deletes a service.
    :param service_id: id
    :return: user object
    """
    deleted = False
    r = self.api_request(method="delete",
                         endpoint="services/{id}".format(id=service_id),
                         response_type="text",
                         headers=self.HEADERS)
    if r == "":
      deleted = True
    return deleted

  def delete_user(self, user_id):
    """
    Deletes a user.
    :param user_id: id
    :return: user object
    """
    r = self.api_request(method="delete",
                         endpoint="users/{id}".format(id=user_id),
                         response_type="text",
                         headers=self.HEADERS)

    return r

  def remove_from_oncalls(self, user_email):
    """
    Removes a user from oncalls, and then deletes the user.
    :param email: user email
    :return: bool
    """
    deleted = False
    user_id = self.find_user_id(user_email=user_email)
    if user_id is not None:
      try:
        userdel = json.loads(self.delete_user(user_id=user_id))
        if "error" in userdel:
          for conflict in userdel["error"]["conflicts"]:
            if conflict["type"] == "schedule":
              self.remove_user_from_schedule(schedule_id=conflict["id"], user_id=user_id)
            elif conflict["type"] == "escalation_policy":
              self.remove_user_from_escalation_policy(policy_id=conflict["id"],
                                                      user_id=user_id,
                                                      delete_empty=True)
          userdel = self.delete_user(user_id=user_id)
          if userdel == "":
            deleted = True
      except ValueError:
        deleted = True
    else:
      deleted = True

    return deleted

  def list_oncalls(self, escalation_policy_ids):
    """
    Returns all oncalls.
    :param escalation_policy_ids: list of escalation policy ids
    :return: list of oncalls resources
    """
    params = {"escalation_policy_ids[]": escalation_policy_ids}
    r = self.api_request(method="get",
                         endpoint="oncalls",
                         params=params,
                         headers=self.HEADERS)
    if "oncalls" in r:
      return r["oncalls"]
    else:
      return None
