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
    "3rdparty/python:twitter.common.log",
    "3rdparty/python:Flask",
    "3rdparty/python:Flask-WTF",
    "3rdparty/python:MarkupSafe",
    "3rdparty/python:WTForms",
    "3rdparty/python:gevent",
    "3rdparty/python:greenlet",
    "3rdparty/python:pycrypto",
    "lib:pagerduty",
    "lib:google_api",
    "lib:gunicorn_wrapper",
    "lib:ldap_client"
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
    "3rdparty/python:pycrypto",
    "lib:pagerduty",
    "lib:google_api",
    "lib:ldap_client"
  ],
)

