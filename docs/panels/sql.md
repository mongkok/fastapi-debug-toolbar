## SQLAlchemy

Please make sure to use the *"Dependency Injection"* system as described in the [FastAPI docs](https://fastapi.tiangolo.com/tutorial/sql-databases/#create-a-dependency) and add the `SQLAlchemyPanel` to your panel list:

```py hl_lines="8"
{!src/panels/sqlalchemy.py!}
```

![SQLAlchemy panel](../img/panels/SQLAlchemy.png)

## Tortoise ORM

Add the `TortoisePanel` to your panel list:

```py hl_lines="8"
{!src/panels/tortoise.py!}
```
