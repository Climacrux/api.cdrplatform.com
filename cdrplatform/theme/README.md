# Theme

A place to manage all the static files for theming the website.

## Development

To have Tailwind and the static files automatically updating during development, run the following:

```shell
$ npm run dev
```

## Deployment

When deploying, need to make sure of two things:

1. The build pipeline is run;
1. The generated static assets are collected;

### Building the static files

Simply run the following to build the tailwind CSS and any other static assets.

```shell
$ npm run build
```

Commit these changes (in the `static/theme/` directory) to git.

### Collecting the

When deploying Django, need to gather all the static files from all the apps (e.g. `admin` app and this `theme` app) into one place. Django has a built in command for this so when deploying make sure to run the following:

```shell
$ poetry run ./manage.py collectstatic
```
