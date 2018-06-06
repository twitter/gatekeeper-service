target(
    name = "google_api_tests",
    dependencies = [
        ":google_admin_tests",
        ":google_calendar_tests",
        ":google_controller_tests",
        ":google_drive_tests",
        ":google_gmail_tests",
        ":google_oauth_tests",
    ],
)

python_tests(
    name = "google_oauth_tests",
    sources = ["oauth_tests.py"],
    dependencies = [
        "3rdparty/python:mock",
        "libs:google_api_oauth",
    ],
)

python_tests(
    name = "google_controller_tests",
    sources = ["controller_tests.py"],
    dependencies = [
        "3rdparty/python:mock",
        "libs:google_api_controller",
    ],
)

python_tests(
    name = "google_admin_tests",
    sources = ["admin_tests.py"],
    dependencies = [
        "3rdparty/python:mock",
        "3rdparty/python:pycrypto",
        "libs:google_api_admin",
    ],
)

python_tests(
    name = "google_gmail_tests",
    sources = ["gmail_tests.py"],
    dependencies = [
        "3rdparty/python:mock",
        "libs:google_api_gmail",
    ],
)

python_tests(
    name = "google_drive_tests",
    sources = ["drive_tests.py"],
    dependencies = [
        "3rdparty/python:mock",
        "libs:google_api_drive",
    ],
)

python_tests(
    name = "google_calendar_tests",
    sources = ["calendar_tests.py"],
    dependencies = [
        "3rdparty/python:mock",
        "libs:google_api_calendar",
    ],
)
