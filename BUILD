python_binary(
  name = "gatekeeper",
  source = "gatekeeper.py",
  zip_safe = False,
  dependencies = [
    ":gatekeeper_dependencies",
  ],
)

python_library(
  name = "gatekeeper_dependencies",
  sources = globs("*.py", "templates/*"),
  dependencies = [
    "3rdparty/python:twitter.common.app",
    "3rdparty/python:Flask",
    "3rdparty/python:Flask-WTF",
    "3rdparty/python:MarkupSafe",
    "3rdparty/python:WTForms",
    "3rdparty/python:gevent",
    "libs:gunicorn_wrapper",
    ":runner_dependencies",
  ],
)

python_binary(
  name = "runner",
  source = "runner.py",
  dependencies = [
    ":runner_dependencies",
  ],
)

python_library(
  name = "runner_dependencies",
  sources = globs("runner.py"),
  dependencies = [
    "3rdparty/python:twitter.common.log",
    "libs:helper_functions",
    "libs:google_api",
    "libs:ldap_client",
    "libs:pagerduty",
    "libs:duo"
  ],
)

