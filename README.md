# GateKeeper
---

GateKeeper is a service built to automate the manual steps involved in onboarding, offboarding, or lost asset scenarios. The service will handle the flow of letting internal and external services know that a user needs to be activated, suspended, or deleted.

The backend for this project is built with Flask and Jinja2 templating.

## Sections

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Support](#support)
4. [Authors](#authors)
5. [License](#license)
6. [Security](#security-issues)
7. [To-Do](#to-do)


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
3. Create a copy of the file config.example.yml to config.yml
   and modify the file to reflect your settings and API keys.
```
cd config
cp config.example.yml config.yml
```
4. Run the tests
```
./pants test tests::
```
5. Run the service
```
./pants run :gatekeeper
```

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
* Document the config file options.
