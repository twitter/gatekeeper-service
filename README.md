# GateKeeper

[![status: unmaintained](https://opensource.twitter.dev/status/unmaintained.svg)](https://opensource.twitter.dev/status/#unmaintained)

GateKeeper is a service built to automate the manual steps involved in onboarding, offboarding, or lost asset scenarios. The service will handle the flow of letting internal and external services know that a user needs to be activated, suspended, or deleted.

This project is built with Flask, Gevent, Gunicorn, and Jinja2 templating.  


## Sections

1. [Features](#features)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Logs](#logging)
6. [Support](#support)
7. [Authors](#authors)
8. [License](#license)
9. [Security](#security)
10. [To-Do](#to-do)


## Features

* **Services currently supported:**  
  * LDAP
  * Google Apps (Admin, Gmail, Calendar, Drive)
  * PagerDuty
  * DUO
  
* **Actions currently implemented:**
  * LDAP
    - Used to extract user information, and perform data validation against the GApps directory.
  * Google Admin (Directory)
    - Reset Google apps password 
    - Purge application specific passwords 
    - Purge 3rd party access tokens 
    - Invalidate backup (verification) codes 
    - Move a user to a custom Organizational Unit 
    - Restore a user back to the default "/" OU
  * Google GMail
    - Set Out Of Office message (with a configurable message)
    - Disable IMAP email 
    - Disable POP email
  * Google Calendar
    - Change events ownership (with a configurable assignee) 
    - Delete future dated events (to free up resources like booked meeting rooms, equipment, etc)
  * Google Drive
    - Transfer ownership of files to another user (with regex filtered search)
  * PagerDuty
    - Remove from OnCall rotas
  * DUO Admin
    - Remove user from DUO
  
* **Deployment methods available:**
  * Locally on MacOS/Linux (or a Virtual Machine)
  * Docker container
  * Mesos, via Aurora

## Prerequisites

1. Linux or MacOS  
Linux is highly recommended for a production installation.  
MacOS is also supported, but should only be used on local deployments, or for testing, due to performance and security concerns.  
Note: If you are installing GateKeeper on MacOS, you will also need to have the XCode Command Line Tools installed:  ``` xcode-select --install ```

2. Python 2.7.x  
You can get it via your package manager, or from [here](https://www.python.org/downloads/).

3. OpenJDK or Oracle JDK 7 or greater  
You can get it via your package manager, or from [OpenJDK](http://openjdk.java.net/install/) or [Oracle](https://www.oracle.com/downloads/index.html) respectively.

4. Bower  
You can get it via your package manager, or from [here](https://bower.io/).

## Installation

#### Initial Configuration 
These steps apply to all the deployment methods listed below, and will need to be executed first.

1. Clone this repository.
   ```
   git clone https://github.com/twitter/gatekeeper-service
   ```

2. You will need an Admin User for GApps, to be able to run GateKeeper operations.  
This can be achieved either by using a Super Admin User, or by creating a Custom Administration Role for the service.  
The latter is highly recommended, as it is a much more secure way of restricting access to your GApps environment.  
You can create a Custom Administration Role, by following the instructions [here](https://support.google.com/a/answer/2406043?hl=en).
   
3. For GateKeeper to be able to act as a user under your domain, you will need a Service Account with Domain-Wide Delegation of Authority.  
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
   Once complete, place your google_api_service_account_keyfile.json file in the config/ folder.
   
4. Create an OrgUnit in your GApps space, where you will be sending your offboarded users to.  
This is good practice, and allows for easy move of an offboarded user back to the org, if necessary.  
You can find instructions on how to add an OU [here](https://support.google.com/a/answer/182537?hl=en). 

5. Create a copy of the file config.example.yml to config.yml and modify the file to reflect your settings and API keys.  
Consult the [Configuration](#configuration) section below for a short description of their usage.  
Note: It is advisable to create separate configs for your test, and production environments.
   ```
   cd config
   cp config.example.yml config.yml
   ```

#### Docker
The following instructions will help you create and launch a Docker container of GateKeeper.

1. Build the Docker image.
   ```
   docker build -t twitter/gatekeeper .
   ```

2. Create and execute a Docker container.
   ```
   docker run -d -p 5000:5000 --name="gatekeeper" twitter/gatekeeper
   ```
   Wait until the service is up. (You can monitor the logs with ```docker logs -f gatekeeper```)  
   You can then access the GateKeeper UI at ```<container_ip>:5000``` (or the port you specified above, if different).  
   
3. You can start/stop/restart the service, with:
   ```
   docker start|stop|restart gatekeeper
   ```

4. _(Optional)_ Remove any untagged or intermediary images created during the build process. 
   ```
   docker image prune
   ```

#### Local/VM Install 
The following instructions will help you launch an instance of GateKeeper locally, or a Virtual Machine.

1. Run the following command to install the javascript package dependencies.
   ```
   cd static
   bower install
   ```

2. Run the tests
   ```
   ./pants test tests::
   ```

3. Run the service
   ```
   ./pants run :gatekeeper
   ```
   You can then access the GateKeeper UI at ```localhost:5000```
   
## Configuration

```yaml
defaults:
  debug:                      bool   (use for troubleshooting. default: false)
  base_dir:                   string (base dir path. default: ".")
  http_proxy:
    use_proxy:                bool   (for routing traffic via a proxy. default: false)
    proxy_url:                string (http proxy url, without the 'http(s)://' prefix)
    proxy_port:               int    (default: 8080)
    proxy_user:               string (http proxy account username)
    proxy_pass:               string (http proxy account password)

ldap:
  base_dn:                    string (base dn for your LDAP)
  uri:                        string (prefixed with "ldap(s)://")
  user:                       string (username for LDAP login)
  pass:                       string (password for LDAP login)
  queries:
    all_users:                string (LDAP query to return all active users. example: "(|(gidNumber=1000) (gidNumber=1001))". Leave empty when testing.)
    user_is_valid:            string (LDAP query to return whether a user is valid, use "USER" as a var. example: "(& (uid=USER) (|(gidNumber=1000) (gidNumber=1001)))")
    user_is_active:           string (LDAP query to return whether a user is active, use "USER" as a var. example: "(& (uid=USER) (gidNumber=1001))")
    user_info:                string (LDAP query to return user attributes, use "USER" as a var. example: "(uid=USER)")
  fields:
    full_name:                string (LDAP field for full name. example: "cn")
    first_name:               string (LDAP field for first nane. example: "givenName")
    role:                     string (LDAP field for role.)
    team:                     string (LDAP field for team.)
    org:                      string (LDAP field for org.)
    location:                 string (LDAP field for location.)
    start_date:               string (LDAP field for start date.)
    uid_number:               string (LDAP field for uid. example: "uidNumber")
    groups:                   string (LDAP field for LDAP groups a user is a member of. example: "memberOf")
    photo_url:                string (Optional - LDAP field for a user's profile photo/avatar location.)

pagerduty:
  base_url:                   string (default: "https://api.pagerduty.com/")
  api_key:                    string (API Key for PagerDuty. Must be v2, and have R/W permissions.)
  
duo:
  host:                       string (Hostname to the DUO Secure server.)
  ikey:                       string (Integration Key for DUO Secure.)
  skey:                       string (Secure Key for DUO Secure.) 
  ca_certs:                   string (Custom SSL Certs location for use with DUO. Leave empty to use the default certs. default: "")

google_apps:
  admin_user:                 string (GApps Account that will own and run the service. See the Installation section for more info. example: "gatekeeper-admin")
  offboarded_ou:              string (GApps OrgUnit where the offboarded users will fall under. default: "/Offboarded Users")
  domain:                     string (Your GApps domain. example: "somedomain.com")
  credentials_keyfile:        string (default: "config/google_api_service_account_keyfile.json")
```

## Logging

Logs are stored under /var/tmp, and will persist system reboots.  
If you are running GateKeeper on Docker, you can also get to the access logs with ```docker logs -f gatekeeper```  
Be sure to include the relevant log line(s) with any issues submitted.

## Support

Please create an issue on GitHub

## Authors

* Harry Kantas <https://github.com/harrykantas>
* Mat Clinton <https://github.com/matc>

Follow [@twitteross](https://twitter.com/twitteross) on Twitter for updates.

## License

Copyright 2013-2018 Twitter, Inc.

Licensed under the Apache License, Version 2.0: https://www.apache.org/licenses/LICENSE-2.0

## Security

Please report sensitive security issues via Twitter's bug-bounty program (https://hackerone.com/twitter).

Be mindful of the file ownership and permissions for your "google_api_service_account_keyfile.json" and "config.yml" files.  
These files will contain sensitive data that can grant API access to your platform and services.  
Please practise caution when choosing a deployment method to better suit your environment's security conditions.

The WebUI is currently served in HTTP, since this service is meant to be deployed within your internal network.  
If your use case requires accessing GateKeeper via HTTPS, that can be achieved by redirecting all traffic to HTTPS with your own public facing proxy. 

## To-Do

* Implement more services.
* Integration with JIRA and other ticketing systems.
* Add the option to parse a batch of users at once, via a CSV file.
* Expose a REST API for services to talk to GateKeeper directly.
* Make the service independent to the presence of LDAP, for orgs that do not make use of it.
