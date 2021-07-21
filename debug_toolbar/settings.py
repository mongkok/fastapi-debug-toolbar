import typing as t

from jinja2 import BaseLoader, ChoiceLoader, Environment, PackageLoader
from jinja2.ext import Extension
from pydantic import BaseSettings, root_validator


class DebugToolbarSettings(BaseSettings):
    PANELS: t.Sequence[str] = [
        "debug_toolbar.panels.versions.VersionsPanel",
        "debug_toolbar.panels.timer.TimerPanel",
        "debug_toolbar.panels.settings.SettingsPanel",
        "debug_toolbar.panels.request.RequestPanel",
        "debug_toolbar.panels.headers.HeadersPanel",
        "debug_toolbar.panels.routes.RoutesPanel",
        "debug_toolbar.panels.logging.LoggingPanel",
        "debug_toolbar.panels.profiling.ProfilingPanel",
        "debug_toolbar.panels.redirects.RedirectsPanel",
    ]
    DISABLE_PANELS: t.Sequence[str] = [
        "debug_toolbar.panels.redirects.RedirectsPanel",
    ]
    ALLOWED_IPS: t.Optional[t.Sequence[str]] = None
    JINJA_ENV: Environment = Environment()
    JINJA_LOADERS: t.List[BaseLoader] = []
    JINJA_EXTENSIONS: t.Sequence[t.Union[str, t.Type[Extension]]] = []
    STATIC_URL: str = "/_debug_toolbar/static"
    API_URL: str = "/_debug_toolbar"
    SHOW_TOOLBAR_CALLBACK: str = "debug_toolbar.middleware.show_toolbar"
    INSERT_BEFORE: str = "</body>"
    SHOW_COLLAPSE: bool = False
    ROOT_TAG_EXTRA_ATTRS: str = ""
    RESULTS_CACHE_SIZE: int = 25
    PROFILER_OPTIONS: t.Dict[str, t.Any] = {"interval": 0.0001}

    def __init__(self, **settings: t.Any) -> None:
        super().__init__(**settings)
        loaders = self.JINJA_LOADERS + [PackageLoader("debug_toolbar", "templates")]
        self.JINJA_ENV.loader = ChoiceLoader(loaders)
        for extension in self.JINJA_EXTENSIONS:
            self.JINJA_ENV.add_extension(extension)

    @root_validator(pre=True)
    def ci(cls, values: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
        return {k.upper(): v for k, v in values.items()}
