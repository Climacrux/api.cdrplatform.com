# CO2 Removal Platform API

A platform for carbon dioxide removal from [Climacrux LLC](https://climacrux.com).

## Configuration

We follow the standard Django pattern and use `settings.py` to manage all settings with the addition of `django-environ` to help customize for each environment.

`django-environ` will automatically read in a `.env` file which contains some default settings.

When developing, the easiest thing to do is create a copy of or link between `.env` and the `.env.dev` file and then adjust these environment variables as needed.

```shell
$ # Copy the file completely
$ cp .env.dev .env

$ # or create a link between the files
$ ln -s .env.dev .env
```

## Development

Getting started with development begins by cloning this repo. Then there are a couple of options to take. Using [dev containers](https://containers.dev/) or not.

To try and create replicable, local development environments, we recommend using dev containers and have provided a `.devcontainer/devcontainer.json` file for exactly that. Using dev containers will automatically create a local development environment with the same versions of Python+dependencies, same tooling and same VS Code extensions.

Dev containers are currently only useful if you use VSCode as your editor.

*Note: Usage of dev-containers with Docker Desktop for Linux can cause some file permissions issues*

Make sure you have the following installed:

- Docker + Docker compose;
- VSCode + [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers);

Upon opening the repository in VSCode you should be prompted to 'reopen in container' (otherwise it can be found under the command palette). This will take a while in the beginning to pull all the docker images but should open a VSCode window, connected to the source code inside the container.

You should now have a development environment running Django+Postgres+Redis and can develop as normal - including running migrate commands etc. - from within the VSCode window.

### Without dev containers

If you do not wish to use development containers, ensure you have Python3.11 on your machine and install the dependencies.

We use [Poetry](hon-poetry.org/docs/) to manage a virtual environment and dependencies.

> Note: If you are having trouble installing `psycopg2` one possible solution is set the correct `LDFLAGS` for SSL.
>
> Example on Mac with Homebrew: `export LDFLAGS="-L/opt/homebrew/opt/openssl@3/lib"`

```shell
$ # Install the dependencies with poetry
$ poetry install
```

### Finish your setup

Regardless of if you chose to use dev containers or not, the following commands are used to finalize the setup:

```shell
$ # install the pre-commit hooks
$ poetry run pre-commit install

$ # run the database migrations
$ poetry run python ./manage.py migrate

$ # start the development server
$ poetry run python ./manage.py runserver

$ # Done when needing a superuser
$ poetry run python ./manage.py createsuperuser
```

### Trying out requests to the API

It's up to you, the developer, as to how you want to

However if you use [VSCode REST Client](https://marketplace.visualstudio.com/items?itemName=humao.rest-client), we provide a series of `.rest` files in the `rest-examples` directory.

## Loading data into the database

We have some [fixtures](https://docs.djangoproject.com/en/4.1/howto/initial-data/) to make it easy for Django to load data into the database for production & testing purposes.

> **Warning:** Loading a fixture will replace any changes that have been made in the database but are not present in the fixture. From the docs: "Each time you run `loaddata`, the data will be read from the fixture and reloaded into the database. Note this means that if you change one of the rows created by a fixture and then run `loaddata` again, you’ll wipe out any changes you’ve made."

```shell
$ # Example: Load the `removal_methods` data
$ poetry run python ./manage.py loaddata removal_methods_partners
```

## UI, design and theme

_See the [`cdrplatform/theme/README.md`](cdrplatform/theme/README.md)_

## Deployment

*todo: deployment instructions using ansible+podman*

### Application monitoring

We use new relic. When running on production ensure to run with following commands:

```shell
$ NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program
```

### Backups

Database backups are performed by [Borg](https://borgbackup.readthedocs.io/en/stable/) with the help of [Borgmatic](https://torsion.org/borgmatic/) using a cron job scheduled to run every 15 minutes:

```cron
*/15 * * * * root PATH=$PATH:/usr/bin:/usr/local/bin borgmatic --verbosity -1 --syslog-verbosity 1
```

Backups are encrypted and pushed to [Borgbase](https://www.borgbase.com/).

## Contact

If you want to discuss CO2 removal; want to add [CDR Platform](https://cdrplatform.com) to your business;
or are a carbon dioxide remover, please contact [Ewan Jones](mailto://ewan@cdrplatform.com).
