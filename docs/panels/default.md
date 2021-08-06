Here's a list of default panels available:

## Versions

![Versions panel](../img/panels/Versions.png)

## Timer

![Timer panels](../img/panels/Timer.png)

## Settings

![Settings panel](../img/panels/Settings.png)

Add your pydantic's [BaseSettings](https://pydantic-docs.helpmanual.io/usage/settings/) classes to this panel:

```py hl_lines="11"
{!src/panels/settings.py!}
```

## Request

![Request panel](../img/panels/Request.png)

## Headers

![Headers panel](../img/panels/Headers.png)

## Routes

![Routes panel](../img/panels/Routes.png)

## Logging

![Logging panel](../img/panels/Logging.png)

## Profiling

![Profiling panel](../img/panels/Profiling.png)

Profiling reports provided by [Pyinstrument](https://github.com/joerick/pyinstrument), you can configure the [profiler parameters](https://pyinstrument.readthedocs.io/en/latest/reference.html#pyinstrument.Profiler) by adding `profiler_options` settings:

```py hl_lines="5"
{!src/panels/profiling.py!}
```

