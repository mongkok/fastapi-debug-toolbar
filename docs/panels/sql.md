## SQLAlchemy

Add the `SQLAlchemyPanel` to your panel list:

```py hl_lines="8"
{!src/panels/sqlalchemy/panel.py!}
```

![SQLAlchemy panel](../img/panels/SQLAlchemy.png)

This panel records all queries using the *"Dependency Injection"* system as described in the [FastAPI docs](https://fastapi.tiangolo.com/tutorial/sql-databases/#create-a-dependency).

If you don't use dependencies then create a new class that inherits from `SQLAlchemyPanel`, override the `add_engines` method and add the class path to your panel list:

```py hl_lines="8 9"
{!src/panels/sqlalchemy/add_engines.py!}
```

# ::: debug_toolbar.panels.sqlalchemy.SQLAlchemyPanel
    handlers: python
    options:
      heading_level: 3
      show_bases: false
      show_root_heading: true
      members:
        - add_engines


## Tortoise ORM

Add the `TortoisePanel` to your panel list:

```py hl_lines="8"
{!src/panels/tortoise.py!}
```
