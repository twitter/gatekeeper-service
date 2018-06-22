import string
import hashlib
from datetime import datetime, timedelta

import yaml
from Crypto.Random import random

APP_CONFIG = 'config/config.yml'


class HelperFunctions(object):
  @classmethod
  def read_config_from_yaml(cls, filename=APP_CONFIG):
    config = None
    with open(filename, "r") as stream:
      try:
        config = yaml.load(stream)
      except yaml.YAMLError as e:
        print(e)
    return config

  @classmethod
  def password_gen(cls):
    chars = string.letters + string.digits
    pwd_length = 50
    return ''.join((random.choice(chars)) for x in range(pwd_length))

  @classmethod
  def hash_passwd(cls):
    password = hashlib.sha1(cls.password_gen()).hexdigest()
    return password

  @classmethod
  def date_now(cls):
    now = datetime.utcnow().isoformat() + 'Z'
    return now

  @classmethod
  def date_less_one_week(cls):
    last_week = (datetime.utcnow() - timedelta(weeks=1)).isoformat() + 'Z'
    return last_week

  @classmethod
  def rfc_datetime_now(cls):
    date_time = cls.date_now().split('.')[0]
    rrule_time = date_time.translate(None, '-:') + 'Z'
    until_time = "UNTIL=" + rrule_time
    return until_time

  @classmethod
  def updated_event_rule(cls, rrule):
    rule_list = []
    rule_ends = False
    for rule in rrule:
      if rule.startswith("RRULE"):
        updated_rule = []
        for item in rule.split(';'):
          if item.startswith('UNTIL') or item.startswith('COUNT'):
            rule_ends = True
            updated_rule.append(cls.rfc_datetime_now())
          else:
            updated_rule.append(item)
        if not rule_ends:
          updated_rule.append(cls.rfc_datetime_now())
        rule_list.append(";".join(updated_rule))
      else:
        rule_list.append(rule)
    return rule_list
