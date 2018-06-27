target(
    name = "tests",
    dependencies = [
        ":google_api",
        ":pagerduty_api",
        ":duo_api",
    ],
)

target(
    name = "google_api",
    dependencies = [
        "tests/libs/google:google_api_tests",
    ],
)

target(
    name = "pagerduty_api",
    dependencies = [
        "tests/libs/pagerduty:pagerduty_tests",
    ],
)

target(
    name = "duo_api",
    dependencies = [
        "tests/libs/duo:duo_tests",
    ],
)
