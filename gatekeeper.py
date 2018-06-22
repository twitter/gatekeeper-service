from gevent import monkey
monkey.patch_all()  # flake8: noqa

from gunicorn_wrapper import StandaloneApplication
from runner import Runner, NO_SUSPEND_ACTIONS
from sse import ServerSentEvent
from forms import OffboardForm, LostAssetForm, FilesOwnershipTransferForm
from helper_functions import HelperFunctions
from ldap_client import LDAPClient, LdapSyncThread

import twitter.common.app as app
import twitter.common.log as log

import gevent
from gevent.queue import Queue

from flask import Flask, flash, redirect, render_template, request, Response, url_for

from datetime import timedelta
import json
import os
import platform


app.set_name = "gatekeeper"
app.add_option("-p", "--port", type="int", default=5000)
config = HelperFunctions().read_config_from_yaml()

PLATFORM = platform.system()

GOOGLE_ADMIN_ACTIONS = list(k for k,v in config["actions"]["google_admin"].items() if v is True)
GOOGLE_GMAIL_ACTIONS = list(k for k,v in config["actions"]["google_gmail"].items() if v is True)
GOOGLE_CALENDAR_ACTIONS = list(k for k,v in config["actions"]["google_calendar"].items() if v is True)
GOOGLE_DRIVE_ACTIONS = list(k for k,v in config["actions"]["google_drive"].items() if v is True)
PAGERDUTY_ACTIONS = list(k for k,v in config["actions"]["pagerduty"].items() if v is True)
DUO_ACTIONS = list(k for k,v in config["actions"]["duo"].items() if v is True)

OFFBOARD_ACTIONS = list(k for k,v in config["action_groups"]["offboard"].items() if v is True)
LOST_ASSET_ACTIONS = config["action_groups"]["lost_asset"]

SET_DEBUG = config["defaults"]["debug"]
BASE_DIR = os.path.abspath(config["defaults"]["base_dir"])

TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Flask config
webapp = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
webapp.config["SECRET_KEY"] = os.urandom(20)
webapp.config["PERMANENT_SESSION_LIFETIME"] = timedelta(seconds=120)

# LDAP Connection
ldap_client = LDAPClient(config=config["ldap"])

# thread is scheduled to sync every 6 hours
t = LdapSyncThread(21600, ldap_client.sync_users)
t.start()

if config["ldap"]["queries"]["all_users"] == "":
  ldap_users = ["harry", "paul", "dave", "adam", "larry"]
else:
  ldap_users = ldap_client.sync_users()

# This is the global hash map where we will store all queues
subscriptions = {}


# TODO(): flash a message if oauth token is invalid.
@webapp.route("/offboard/<string:session_id>", methods=["POST"])
def offboard_post(session_id):
  log.info("publish: %s" % session_id)
  lost_asset = False
  admin_api_actions = []
  gmail_api_actions = []
  gcal_api_actions = []
  pagerduty_actions = []
  duo_actions = []
  user_id = request.form.get("USER_ID")
  for (k, v) in request.form.items():
    if k in GOOGLE_ADMIN_ACTIONS:
      admin_api_actions.append(k.lower())
    elif k in GOOGLE_GMAIL_ACTIONS:
      gmail_api_actions.append(k.lower())
    elif k in GOOGLE_CALENDAR_ACTIONS:
      gcal_api_actions.append(k.lower())
    elif k in PAGERDUTY_ACTIONS:
      pagerduty_actions.append(k.lower())
    elif k in DUO_ACTIONS:
      duo_actions.append(k.lower())
    elif k == "LOST_ASSET":
      lost_asset = True

  def run(runner, connector, action, kwargs):
    if session_id not in subscriptions:
      subscriptions[session_id] = Queue()
      log.info("adding new queue to map: %s" % subscriptions)
    sub = subscriptions[session_id]
    params = {"runner": runner, "connector": connector, "action": action, "params": kwargs}
    sub.put(params)
    log.info("adding to queue: %s" % params)

  # TODO(): move this logic on the runner.
  def change_events_ownership(runner, grantee_user_id):
    if session_id not in subscriptions:
      subscriptions[session_id] = Queue()
      log.info("adding new queue to map: %s" % subscriptions)
    sub = subscriptions[session_id]
    runner_grantee = Runner(user=grantee_user_id)
    if runner_grantee.is_suspended_user:
      runner_grantee.suspend_user(False)
    moved_events = {}
    calendar_id = runner.calendar_api.get_calendar_id()
    grantee_calendar_id = runner_grantee.calendar_api.get_calendar_id()
    if calendar_id is not None and grantee_calendar_id is not None:
      runner.calendar_api.move_calendar_ownership(grantee_calendar_id)
      runner_grantee.calendar_api.move_calendar_ownership(calendar_id)
      events = runner.calendar_api.list_events(calendar_id)
      if events:
        for event in events:
          result = runner.calendar_api.move_event(event, grantee_calendar_id)
          if result is True:
            value = "<span class='text-success'>%s</span>" % result
          elif v is False:
            value = "<span class='text-danger'>%s</span>" % result
          else:
            value = result
          moved_events[event] = value
    sub.put({"change_events_ownership": moved_events})
    log.info("adding to queue: %s" % moved_events)

  runner = Runner(user=user_id)
  if lost_asset:
    runner.suspend_user(True)
    runner.suspend_user(False)
    log.info("lost_asset - resetting sign-in cookies")
    gevent.spawn(run, runner, "admin_api", "lost_asset", {})
  for action in admin_api_actions:
    gevent.spawn(run, runner, "admin_api", action, {})
    log.info("spawned action: %s" % action)
  for action in gmail_api_actions:
    if action == "set_ooo_msg":
      ooo_msg_text = request.form.get("OOO_MSG_TEXT")
      params = {"text": ooo_msg_text}
      gevent.spawn(run, runner, "gmail_api", action, params)
    else:
      gevent.spawn(run, runner, "gmail_api", action, {})
    log.info("spawned action: %s" % action)
  for action in gcal_api_actions:
    if action == "change_events_ownership":
      grantee_user_id = request.form.get("GCAL_NEW_OWNER")
      if grantee_user_id:
        grantee_user_id_is_valid = ldap_client.is_valid_user(grantee_user_id)
        if grantee_user_id_is_valid:
          gevent.spawn(change_events_ownership(runner, grantee_user_id))
    else:
      gevent.spawn(run, runner, "calendar_api", action, {})
      log.info("spawned action: %s" % action)
  for action in pagerduty_actions:
    gevent.spawn(run, runner, "pagerduty_api", action, {})
    log.info("spawned action: %s" % action)
  for action in duo_actions:
    gevent.spawn(run, runner, "duo_api", action, {})
    log.info("spawned action: %s" % action)
  return "OK"


@webapp.route("/offboard/<string:session_id>", methods=["GET"])
def offboard_get(session_id):
  log.info("stream: %s" % session_id)
  if session_id in subscriptions:
    def gen(session_id):
      q = subscriptions[session_id]
      q_size = len(q)
      log.info("pulling queue: %s" % q)
      runner = None
      suspend_user = True
      while not q.empty():
        r = q.get()
        log.info("pulling from queue: %s" % r)
        if "action" in r.keys():
          # do not suspend if we are only performing non-google apps actions
          if r["action"] in NO_SUSPEND_ACTIONS and q_size == 1:
            suspend_user = False
          # do not suspend the user if we are setting an ooo msg
          if r["action"] == "set_ooo_msg":
            suspend_user = False
          # do not suspend the user if we are resetting due to lost asset
          if r["action"] == "lost_asset":
            suspend_user = False
        # handle output for calendar events ownership
        if "change_events_ownership" in r.keys():
          value = r["change_events_ownership"]
          if value:
            result = "<p>CHANGE EVENTS OWNERSHIP: %s</p>" % value
          else:
            result = "<p>CHANGE EVENTS OWNERSHIP: <span class='text-success'>SUCCESS</span></p>"
        elif r["action"] != "lost_asset":
          runner = r["runner"]
          result = runner.perform_action(r["connector"], r["action"], r["params"])
        else:
          result = "<p>RESET SIGN-IN COOKIES: <span class='text-success'>SUCCESS</span></p>"
        log.info("result: %s" % result)
        ev = ServerSentEvent(str(result))
        yield ev.encode()
      if runner is not None:
        suspend = runner.suspend_user(True)
        log.info("suspend: %s" % suspend)
        if not suspend_user:
          suspend = runner.suspend_user(False)
          log.info("un-suspend: %s" % suspend)
      del subscriptions[session_id]
      log.info("removing queue: %s" % q)
    return Response(gen(session_id), mimetype="text/event-stream")
  else:
    def error():
      err = ""
      ev = ServerSentEvent(err)
      yield ev.encode()
    return Response(error(), mimetype="text/event-stream")


@webapp.route("/", methods=["GET", "POST"])
def index():
  # TODO(): implement authentication mechanism
  user = "GateKeeper"
  log.info("Accessed by: %s" % user)

  form = OffboardForm()
  user_info = None

  if request.method == "POST":
    user_id = form.data["USER_ID"]
    try:
      user_is_valid = ldap_client.is_valid_user(user_id)
      if user_is_valid:
        user_info = ldap_client.get_user_info(user_id)
        user_info["active"] = ldap_client.is_active_user(user_id)
        default_ooo_msg = ("Hello. I no longer work here. Please resend your message to %s. "
                           "Thank you" % (user_info["manager"]))
        form.OOO_MSG_TEXT.data = default_ooo_msg
      else:
        flash("WARNING: %s is not a valid LDAP user." % user_id)
        return redirect(url_for('index'))
    except AttributeError:
      flash("WARNING: %s is not a valid LDAP user." % user_id)
      return redirect(url_for('index'))

  return render_template("index.html",
                         form=form,
                         users=json.dumps(ldap_users),
                         user=user,
                         user_info=user_info,
                         ldap_fields=config["ldap"]["fields"],
                         google_admin_actions=GOOGLE_ADMIN_ACTIONS,
                         google_gmail_actions=GOOGLE_GMAIL_ACTIONS,
                         google_calendar_actions=GOOGLE_CALENDAR_ACTIONS,
                         pagerduty_actions=PAGERDUTY_ACTIONS,
                         duo_actions=DUO_ACTIONS)


@webapp.route("/lost_asset", methods=["GET", "POST"])
def lost_asset():
  try:
    cookie = request.elfowl_cookie
    user = cookie.user
  except AttributeError:
    user = "demo"
  log.info("Accessed by: %s" % user)

  form = LostAssetForm()
  user_info = None

  if request.method == "POST":
    user_id = form.data["USER_ID"]
    try:
      user_is_valid = ldap_client.is_valid_user(user_id)
      if user_is_valid:
        user_info = ldap_client.get_user_info(user_id)
        user_info["active"] = ldap_client.is_active_user(user_id)
      else:
        flash("WARNING: %s is not a valid LDAP user." % user_id)
        return redirect(url_for('lost_asset'))
    except AttributeError:
      flash("WARNING: %s is not a valid LDAP user." % user_id)
      return redirect(url_for('lost_asset'))

  return render_template("lost_asset.html",
                         form=form,
                         users=json.dumps(ldap_users),
                         user=user,
                         user_info=user_info,
                         ldap_fields=config["ldap"]["fields"],
                         actions=LOST_ASSET_ACTIONS)


@webapp.route("/gdrive", methods=["GET", "POST"])
def gdrive():
  try:
    cookie = request.elfowl_cookie
    user = cookie.user
  except AttributeError:
    user = "demo"
  log.info("Accessed by: %s" % user)

  form = FilesOwnershipTransferForm()
  user_info = None
  files = None

  if request.method == "POST":
    user_id = form.data["USER_ID"]
    user_is_valid = ldap_client.is_valid_user(user_id)

    if user_is_valid:
      user_info = ldap_client.get_user_info(user_id)
      file_search = form.data["FILE_SEARCH"]
      new_owner = form.data["NEW_OWNER"]
      files = []
      runner = Runner(user=user_id)

      if new_owner:
        new_owner_is_valid_user = ldap_client.is_valid_user(new_owner)
        if new_owner_is_valid_user:
          files = runner.drive_api.search_files_list(drive_query=file_search)
          runner_new_owner = Runner(user=new_owner)
          runner.suspend_user(False)
          runner_new_owner.suspend_user(False)
          for file in files:
            if file["id"] in request.form.keys():
              result = str(runner
                           .drive_api
                           .transfer_file_owner(file["id"], runner_new_owner.user_email))
              file["chown"] = result
              log.info("File Transfer: %s" % (file["chown"]))
          runner.suspend_user(True)

        else:
          flash("WARNING: %s is not a valid LDAP user." % user_id)
          return redirect(url_for('gdrive'))

      elif file_search:
        files = runner.drive_api.search_files_list(drive_query=file_search)

    else:
      flash("WARNING: %s is not a valid LDAP user." % user_id)
      return redirect(url_for('gdrive'))

  return render_template("gdrive.html",
                         form=form,
                         users=json.dumps(ldap_users),
                         user=user,
                         user_info=user_info,
                         ldap_fields=config["ldap"]["fields"],
                         files=files)


def main(args, options):
  if PLATFORM == "Linux":
    StandaloneApplication(wsgi_app=webapp, port=options.port, debug=SET_DEBUG).run()
  elif PLATFORM == "Darwin":
    webapp.run(host="0.0.0.0", port=options.port, debug=SET_DEBUG, threaded=True)

app.main()
