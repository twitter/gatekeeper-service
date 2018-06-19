# GateKeeper
---

GateKeeper is a service built to automate the manual steps involved in onboarding, offboarding, or lost asset scenarios. The service will handle the flow of letting internal and external services know that a user needs to be activated, suspended, or deleted.

The backend for this project is built with Flask and Jinja2 templating.  


## Sections

1. [Features](#features)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Logs](#logging)
6. [Support](#support)
7. [Authors](#authors)
8. [License](#license)
9. [Security](#security-issues)
10. [To-Do](#to-do)


## Features

GateKeeper will run on MacOS and Linux.

* Services currently supported:  
  * LDAP
  * Google Apps (Admin, Gmail, Calendar, Drive)
  * PagerDuty
  * DUO
  
* Deployment methods available:
  * local (or a Virtual Machine)
  * Mesos, via Aurora
  * Docker container

## Prerequisites

1. Linux or MacOS  
If you are installing GateKeeper on MacOS, you will also need to have the XCode Command Line Tools installed:  ``` xcode-select --install ```

2. Python 2.7.x  
You can get it via your package manager, or from [here](https://www.python.org/downloads/).

3. OpenJDK or Oracle JDK 7 or greater  
You can get it via your package manager, or from [OpenJDK](http://openjdk.java.net/install/) or [Oracle](https://www.oracle.com/downloads/index.html) respectively.

4. Bower  
You can get it via your package manager, or from [here](https://bower.io/).

## Installation

The following instructions will help you launch an instance of GateKeeper locally.

1. Clone this repository.
   ```
   git clone https://github.com/twitter/gate-keeping-service
   ```

2. Run the following command to install the javascript package dependencies.
   ```
   cd static
   bower install
   ```

3. Create a copy of the file config.example.yml to config.yml and modify the file to reflect your settings and API keys.  
Consult the comments on each parameter in the config file, for a short description of their usage.
   ```
   cd config
   cp config.example.yml config.yml
   ```

4. For GateKeeper to be able to act as a user under your domain, you will need a Service Account with Domain-Wide Delegation of Authority.  
Click [here](https://developers.google.com/admin-sdk/directory/v1/guides/delegation) for a guide on how to obtain these credentials.  
(Follow the guides under sections "Create the service account and its credentials", and "Delegate domain-wide authority to your service account")  
A list of scopes needed for GateKeeper's operations can be found on the config.example.yml file:
   ```
   - "https://www.googleapis.com/auth/admin.directory.user"
   - "https://www.googleapis.com/auth/admin.directory.user.security"
   - "https://www.googleapis.com/auth/admin.directory.group.member"
   - "https://www.googleapis.com/auth/gmail.settings.basic"
   - "https://www.googleapis.com/auth/gmail.settings.sharing"
   - "https://www.googleapis.com/auth/calendar"
   - "https://www.googleapis.com/auth/drive"
   ```
   Once complete, place your google_api_service_account_keyfile.json file in config folder.

4. Run the tests
   ```
   ./pants test tests::
   ```

5. Run the service
   ```
   ./pants run :gatekeeper
   ```

## Configuration

```yaml
defaults:
  base_dir:                   string (base dir path)
  use_https:                  bool
  debug:                      bool
  flask_secret:               string
  http_proxy:
    use_proxy:                bool
    proxy_url:                string
    proxy_port:               int
    proxy_user:               string
    proxy_pass:               string

ldap:
  base_dn:                    string
  uri:                        string (prefixed with "ldap(s)://")
  user:                       string
  pass:                       string
  queries:
    all_users:                string
    user_is_valid:            string
    user_is_active:           string
    user_info:                string (example: "(uid=USER)")
  fields:
    full_name:                string (example: "cn")
    first_name:               string (example: "givenName")
    role:                     string
    team:                     string
    org:                      string
    location:                 string
    start_date:               string
    uid_number:               string (example: "uidNumber")
    groups:                   string (example: "memberOf")
    photo_url:                string (optional)

pagerduty:
  base_url:                   string (example: "https://api.pagerduty.com/")
  api_key:                    string
  
duo:
  host:                       string
  ikey:                       string
  skey:                       string
  ca_certs:                   string

google_apps:
  admin_user:                 string
  domain:                     string
  credentials_keyfile:        string (example: "google_api_service_account_keyfile.json")
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

* Implement more services.
* Provide more deployment options (Docker container currently WIP).
* Expose a REST API for services to talk to GateKeeper directly.
