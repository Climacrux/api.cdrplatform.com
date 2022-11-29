# CO2 Removal Platform API

A platform for carbon dioxide removal from [Climacrux LLC](https://climacrux.com).

## Configuration

## Installing Dependencies

We use [Poetry](hon-poetry.org/docs/) to manage a virtual environment and dependencies.

> Note: If you are having trouble installing `psycopg2` one possible solution is set the correct `LDFLAGS` for SSL.
>
> Example on Mac with Homebrew: `export LDFLAGS="-L/opt/homebrew/opt/openssl@3/lib"`

```shell
$ # Install the dependencies with poetry
$ poetry install
```

## Development

Clone this repo and install the dependencies (info above).

```shell
$ # install the pre-commit hooks
$ poetry run pre-commit install

$ # run the database migrations
$ poetry run ./manage.py migrate

$ # start the development server
$ poetry run ./manage.py runserver

$ # Done when needing a superuser
$ poetry run ./manage.py createsuperuser
```

### Trying out requests to the API

It's up to you, the developer, as to how you want to

However if you use [VSCode REST Client](https://marketplace.visualstudio.com/items?itemName=humao.rest-client), we provide a series of `.rest` files in the `rest-examples` directory.

## Loading data into the database

We have some [fixtures](https://docs.djangoproject.com/en/4.1/howto/initial-data/) to make it easy for Django to load data into the database for production & testing purposes.

> **Warning:** Loading a fixture will replace any changes that have been made in the database but are not present in the fixture. From the docs: "Each time you run `loaddata`, the data will be read from the fixture and reloaded into the database. Note this means that if you change one of the rows created by a fixture and then run `loaddata` again, you’ll wipe out any changes you’ve made."

```shell
$ # Example: Load the `removal_methods` data
$ poetry run ./manage.py loaddata removal_methods_partners
```

## UI, design and theme

_See the [`cdrplatform/theme/README.md`](cdrplatform/theme/README.md)_

## Deployment

_Todo_

### Application monitoring

We use new relic. When running on production ensure to run with following commands:

```shell
$ NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program
```

## Contact

If you want to discuss CO2 removal; want to add [CDR Platform](https://cdrplatform.com) to your business;
or are a carbon dioxide remover, please contact [Ewan Jones](mailto://ewan@cdrplatform.com).
