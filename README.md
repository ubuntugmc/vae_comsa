# VA Explorer Web Application Prototype

VA Explorer is a prototype web application, built to both demonstrate verbal autopsy data management and
analysis capabilities and act as a foundation for exploring new concepts. This prototype represents a
work-in-progress, and is expected to mature in response to feedback from users and subject matter experts.
VA Explorer currently supports the following functionality at various degrees of maturity:

* User account management, including:
  *  Creation/disabling of user accounts by administrators
  *  Password management for individual users
* User access controls, including:
  *  Role-based access with the following roles: administrators, data managers, data viewers, dashboard viewers,
  and field workers
  *  Assignment to one or more geographic areas for geographical-level scoping of data
* Loading of verbal autopsy questionnaire data
* Assignment of cause of death using InterVA5 algorithm (Note: relies on external pyCrossVA and
InterVA5 services)
* Exploration of cause of death data via a dynamic, visualization-based dashboard that includes:
  *  A dynamic heatmap showing geographical trends, with zoom capabilities to hone in on regions
  of interest
  *  Cause of death plots for chosen regions
  *  Death distributions by age, gender, and place of death for chosen regions
  *  Trends over time for chosen regions

<a href="docs/assets/overview.png">
  <img src="docs/assets/overview.png" alt="Overview" title="VA Explorer Overview" width="270" />
</a>Î
<a href="docs/assets/dashboard.png">
  <img src="docs/assets/dashboard.png" alt="Dashboard" title="VA Explorer Dashboard" width="270" />
</a>
<a href="docs/assets/vas.png">
  <img src="docs/assets/vas.png" alt="Verbal Autopsies" title="VA Explorer VAs" width="270" />
</a>Î

## Background

Verbal autopsies (VAs) are structured interviews for determining the most likely cause of death based on
information from caregivers or family members about the signs and symptoms the deceased experienced before
they died. The current VA IT landscape consists of tools and systems that together enable the various
steps of the VA process, from generation and revision of a VA interview questionnaire to the eventual
use of the resulting cause of death data by localities. By directly integrating with existing
functionality, drawing inspiration from others, and combining new features into a cohesive whole,
VA Explorer aims to enable the integration of verbal autopsy into civil registration and vital
statistics systems at scale.

## Installation and Setup for Development or Testing

VA Explorer is a Django web application that uses the PostgreSQL database for data storage.

### Prerequisites

To work with the application, you will need to install some prerequisites:

* [Python 3](https://www.python.org/downloads/)
* [pip](https://pypi.org/project/pip/)
* [Postgres](http://www.postgresql.org/)
* [Docker](https://www.docker.com/)

Once the prerequisites are available, VA Explorer can be installed and demonstration data can be loaded.

### Setup

* Retrieve the application source code

    `git clone https://github.com/VA-Explorer/va_explorer.git`

* Change into the new directory

    `cd va_explorer`

* Create a virtual env

    `python -m venv venv`

* Activate the virtual env:

    `source venv/bin/activate`

* Install application requirements

    `pip install -r requirements/base.txt`

* Create the va_explorer database

    `createdb va_explorer -U <name of Postgres user> --password`

* Create a .env file at the project root with the following key/value pairs:

    *  `DATABASE_URL=psql://<YOUR POSTGRESUSER>:<POSTGRESUSER PASSWORD>@localhost/va_explorer`
    *  `CELERY_BROKER_URL=redis://localhost:6379/0`


* Run the database migrations
    * `./manage.py makemigrations`
    * `./manage.py migrate`

### Tasks

* Manage user accounts

  * Create user roles

    `./manage.py initialize_groups`

  * Create an administrator user for the local environment (note that for the production environment instead of providing the password on the command line a system-assigned, randomly-generated password will be printed to the console)

    `./manage.py seed_admin_user <EMAIL_ADDRESS> --password <PASSWORD>`

  * Create demonstration accounts for data manager, data viewer, and field worker. This task
  only works in the local environment and is for demonstration purposes, only.

    `./manage.py seed_demo_users`

  * Bulk-create users from a csv file.

    `./manage.py bulk_load_users <CSV_FILE> --email-confirmation <True/False>`

    You can specify user emails, roles, location restrictions, and any other restrictions that are currently exposed in the User Creation Form. If `--email-confirmation` is set to `True`, a confirmation email will be sent out to each new user. Otherwise, their credentials (with temporary password) will be printed to the console. To get a starting template for user csv file, you can run the following command:

    `./manage.py get_user_form_template --output_file <FILENAME>`

  * Export anynymous info for all users in system 
    `./manage.py export_user_info --output_file <FILENAME>`
      This will export an anymymous user ID, user roles, geographic restrictions and privileges to a csv file. Can be used to track user activity in logs withou compromising thier PII.

* Load location data

  `./manage.py load_locations <NAME OF CSV>`

* Load verbal autopsy questionnaire data

  `./manage.py load_va_csv <NAME OF CSV>`

* Start the cause of death coding microservices (pyCrossVA for format
  translation and InterVA5 for coding); note that these are services
  that should be left running during development activities, which can
  be accomplished using a separate terminal or the -d flag. (See [Building/Running in Docker](#buildingrunning-in-docker) for more details).

  `docker-compose up --build`

* Run the InterVA5 cause of death coding algorithm (See [Running Coding Algorithm](#running-coding-algorithm) for more details).

  `./manage.py run_coding_algorithms`

* Run the tests

    `pytest`

### Running the Application

* Run the application server

    `./manage.py runserver 0.0.0.0:8000`

The server will be running at http://0.0.0.0:8000/

## Building/Running in Docker

Django can run locally inside Docker. This will also set up postgres and redis and automatically configure `DATABASE_URL` and `CELERY_BROKER_URL` to use the docker images of postgres and redis.

```
docker-compose -f docker-compose.yml -f docker-compose.local.yml up django vapostgres
```

The server will be running at http://0.0.0.0:5000/

### Building for Production

To build a production ready version of all images, run the following:

```
docker-compose build
```

This will build the following docker images:

```
va_explorer/pycrossva
va_explorer/interva5
va_explorer/vapostgres
va_explorer/celeryworker
va_explorer/celerybeat
va_explorer/flower
va_explorer/django
```

### Deploying with a reverse proxy

Set the following environment variables:

```
export EMAIL_URL=smtp://localhost:25 <or> consolemail://
export CELERY_BROKER_URL=redis://redis:6379/0
export REDIS_URL=redis://redis:6379/0
export POSTGRES_HOST=vapostgres
export POSTGRES_PORT=5432
export POSTGRES_DB=va_explorer
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=Pimin73y!we
export DJANGO_SECRET_KEY=something-secret
export DJANGO_ALLOWED_HOSTS=localhost
```

Run docker-compose in daemon mode:

```
docker-compose up -d django
```

If using Apache, set the following configuration in your apache configuration:

```
LoadModule rewrite_module modules/mod_rewrite.so
LoadModule proxy_module modules/mod_proxy.so
LoadModule proxy_http_module modules/mod_proxy_http.so
LoadModule proxy_wstunnel_module modules/mod_proxy_wstunnel.so

<Location />
    ProxyPreserveHost on
    ProxyPass http://localhost:5000/
    ProxyPassReverse http://localhost:5000/

    RewriteEngine on
    RewriteCond %{HTTP:UPGRADE} ^WebSocket$ [NC]
    RewriteCond %{HTTP:CONNECTION} ^Upgrade$ [NC]
    RewriteRule .* ws://localhost:5000%{REQUEST_URI} [P]
</Location>
```

### Creating first user

To create a super user while running under Docker, make sure the container is running, then run the following command to enter a shell in the docker container:

```
docker-compose exec django sh
```

From there, you can create a super user. Follow the prompts after running this command:

```
./manage.py createsuperuser
```

## Running Coding Algorithm

There are two ways to run the coding algorithm to add cause of death to uncoded verbal autopsies: from the command line or from the user interface.

Both methods require the `PYCROSS_HOST` and `INTERVA_HOST` environment variables to be configured to point to the locations of pyCrossVA
InterVA5 respectively. If you are in Docker, both of those will have been configured and started up automatically.

### Command Line

From the command line, you can run the following to run coding algorithms:

```
./manage.py run_coding_algorithms
```

This will list a brief report of results in the following format:

```
Coded 24 verbal autopsies (out of 30) [6 issues]
```

You will receive an error message if pyCrossVA or InterVA5 are unavailable.

### User Interface

Users with permissions to modify verbal autopsy records will see a "Run Coding Algorithms" button on the home page of the application.

In addition to pyCrossVA and InterVA5, this functionality requires that Celery is running and the `CELERY_BROKER_URL` and `REDIS_URL` environment variables have been configured properly. If you are running in Docker, Celery will have been configured and started up automatically.

Clicking the "Run Coding Algorithms" will execute the coding algorithms in the background using Celery. You will not receive an error on the user interface if the process is not successful. To check for errors, you will need to view the Celery logs.

## Importing From ODK

You can use the `import_from_odk` management command to import records from an ODK server like so. 
You must specify either project-name or project-id and form-name or form-id to import:

```
./manage.py import_from_odk --project-id=1234 --form-id=va_form_id
# or
./manage.py import_from_odk --project-name=zambia-test --form_id=va_form_id
# or
./manage.py import_from_odk --project-name=zambia-test --form_name='Form Name'
```

This depends on the following environment variables being set:

```
ODK_HOST=https://odk-server
ODK_EMAIL=example@example.com
ODK_PASSWORD=example
```

Alternatively, you can specify email and pasword as command line arguments:

```
./manage.py import_from_odk --project-name=zambia-test --email=example@example.com --password=example
```

## Version History

This project adheres to [Semantic Versioning](http://semver.org/).

Releases are documented in the [CHANGELOG]().

## License

Copyright 2020-2021 The MITRE Corporation

The source of this information is the Data for Health Initiative, a joint project of the CDC Foundation and Bloomberg Philanthropies.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

```
http://www.apache.org/licenses/LICENSE-2.0
```

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

## Contact Information

For questions or comments about VA Explorer, please send an email to:

```
verbal-autopsy@mitre.org
```
