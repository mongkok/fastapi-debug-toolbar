## First steps

Before writing your own panel you need to provide a [Jinja loader](https://jinja.palletsprojects.com/en/latest/api/#loaders) instance used to load your templates from the file system or other locations.

```py hl_lines="10 11"
{!src/dev/quickstart.py!}
```

## Create a panel

Subclass `Panel` and override `generate_stats()` method to implement a custom panel on your `panels.py`.
This method should return a dict with the panel stats.

```py hl_lines="6 12"
{!src/dev/panels.py!}
```

!!! tip

    The `process_request()` method is **optional** and particularly useful for adding behavior that occurs before the request is processed.

    Please see the [Panel](panel.md) class reference for further details.

## Writing the template

Create a template at `templates/example.html` to display your panel stats:

```html
<span>{{ example }}</span>
```
