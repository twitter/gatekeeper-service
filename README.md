# GateKeeper
---

GateKeeper is a service built to automate the manual steps involved in onboarding, offboarding, or lost asset scenarios. The service will handle the flow of letting internal and external services know that a user needs to be activated, suspended, or deleted.

The backend for this project is built with Flask and Jinja2 templating.

## Sections

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Logs](#logging)
4. [Support](#support)
5. [Authors](#authors)
6. [License](#license)
7. [Security](#security-issues)
8. [To-Do](#to-do)


## Prerequisites

1. Python 2
You can get it via your package manager, or from here: https://www.python.org/downloads/

2. Bower
You can get it via your package manager, or from here: https://bower.io/


## Installation

The following instructions will help you launch an instance of GateKeeper locally.

1. Clone this repository.
```
git clone https://github.com/twitter/gate-keeping-service
```
2. Run the following command to install the javascript package dependencies
```
cd static
bower install
```

3a. Create a copy of the file config.example.yml to config.yml and modify the file to reflect your settings and API keys.
Consult the comments on each parameter in the config file, for a short description of their usage.
```
cd config
cp config.example.yml config.yml
```

3b. For GateKeeper to be able to act as a user under your domain, you will need a Service Account with Domain-Wide Delegation of Authority.
Click [here](https://developers.google.com/admin-sdk/directory/v1/guides/delegation) for a guide on how to obtain these credentials.
(Follow the guides under sections "Create the service account and its credentials", and "Delegate domain-wide authority to your service account")
A list of scopes needed for GateKeeper's operations can be found on the config.example.yml file.
Once complete, place your google_api_service_account_keyfile.json file in config folder.

4. Run the tests
```
./pants test tests::
```
5. Run the service
```
./pants run :gatekeeper
```

## Logging

Logs are stored under /var/tmp, and will persist system reboots.
Be sure to include the relevant log line(s) with any issues submitted.

## Support

Create an issue on GitHub

## Authors

* Harry Kantas <https://github.com/harrykantas>
* Mat Clinton <https://github.com/matc>

Follow [@twitteross](https://twitter.com/twitteross) on Twitter for updates.

## License

Copyright 2013-2018 Twitter, Inc.

Licensed under the Apache License, Version 2.0: https://www.apache.org/licenses/LICENSE-2.0

## Security Issues

Please report sensitive security issues via Twitter's bug-bounty program (https://hackerone.com/twitter).


## To-Do

* Implement more services (DUO currently in testing).
* Expose a REST API for services to talk to directly.
