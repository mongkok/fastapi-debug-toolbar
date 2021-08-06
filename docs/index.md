A debug toolbar for FastAPI based on the original [django-debug-toolbar](https://github.com/jazzband/django-debug-toolbar).

**Swagger UI** & **GraphQL** are supported.

## Requirements

Python 3.6+

## Installation

```sh
pip install fastapi-debug-toolbar
```

!!! info

    The following packages are automatically installed:

    * [Jinja2](https://github.com/pallets/jinja) for toolbar templates.
    * [aiofiles](https://github.com/Tinche/aiofiles) to serve toolbar static files.
    * [pyinstrument](https://github.com/joerick/pyinstrument) for profiling support.

## Quickstart

Add `DebugToolbarMiddleware` middleware to your FastAPI application:

```py
{!src/quickstart.py!}
```

## How it works

Once installed, the debug toolbar is displayed on the right-hand side of your browser.

The middleware add a script into your HTML templates to overwrite the [JSON.parse](https://www.w3schools.com/js/js_json_parse.asp) method. Once a request is sent, the middleware injects the stats into JSON response object to be parsed by this script to automatically update the Debug Toolbar with the new request.

This process allows Debug Toolbar to provide support for [Swagger UI](https://swagger.io/tools/swagger-ui/) and [GraphiQL](https://github.com/graphql/graphiql) among other development tools.

![Swagger UI](img/Swagger.png)
