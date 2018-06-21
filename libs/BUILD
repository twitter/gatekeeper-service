python_library(
    name = "google_api",
    sources = globs("google/*.py"),
    dependencies = [
        ":google_api_admin",
        ":google_api_calendar",
        ":google_api_drive",
        ":google_api_gmail",
        ":google_api_oauth",
    ],
)

python_library(
    name = "google_api_oauth",
    sources = globs("google/oauth.py"),
    dependencies = [
        "3rdparty/python:SocksiPy-branch",
        "3rdparty/python:httplib2",
        "3rdparty/python:oauth2client",
    ],
)

python_library(
    name = "google_api_controller",
    sources = globs("google/controller.py"),
    dependencies = [
        "3rdparty/python:google-api-python-client",
    ],
)

python_library(
    name = "google_api_admin",
    sources = globs("google/admin.py"),
    dependencies = [
        ":google_api_controller",
        ":helper_functions",
    ],
)

python_library(
    name = "google_api_gmail",
    sources = globs("google/gmail.py"),
    dependencies = [
        ":google_api_controller",
        ":helper_functions",
    ],
)

python_library(
    name = "google_api_drive",
    sources = globs("google/drive.py"),
    dependencies = [
        ":google_api_controller",
        ":helper_functions",
    ],
)

python_library(
    name = "google_api_calendar",
    sources = globs("google/calendar.py"),
    dependencies = [
        ":google_api_controller",
        ":helper_functions",
    ],
)

python_library(
    name = "pagerduty",
    sources = globs("pagerduty/*.py"),
    dependencies = [
        ":http_controller",
    ],
)

python_library(
    name = "duo",
    sources = globs("duo/*.py"),
    dependencies = [
        "3rdparty/python:duo-client"
    ],
)

python_library(
    name = "helper_functions",
    sources = globs("helper_functions.py"),
    dependencies = [
        "3rdparty/python:PyYAML",
        "3rdparty/python:pycrypto",
    ],
)

python_library(
    name = "http_controller",
    sources = globs("http_controller.py"),
    dependencies = [
        "3rdparty/python:PyYAML",
        "3rdparty/python:requests",
    ],
)

python_library(
    name = "gunicorn_wrapper",
    sources = globs("gunicorn_wrapper.py"),
    dependencies = [
        "3rdparty/python:gunicorn",
    ],
)

python_library(
    name = "ldap_client",
    sources = globs("ldap_client.py"),
    dependencies = [
        "3rdparty/python:python-ldap",
    ],
)
