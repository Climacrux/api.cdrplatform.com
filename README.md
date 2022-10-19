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
```

## Deployment

_Todo_

## Contact

If you want to discuss CO2 removal; want to add [CDR Platform](https://cdrplatform.com) to your business;
or are a carbon dioxide remover, please contact [Ewan Jones](mailto://ewan@cdrplatform.com).
