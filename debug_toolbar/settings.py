import typing as t

from jinja2 import BaseLoader, ChoiceLoader, Environment, PackageLoader
from jinja2.ext import Extension
from pydantic import BaseSettings, IPvAnyAddress, root_validator
from pydantic.color import Color


class DebugToolbarSettings(BaseSettings):
    DEFAULT_PANELS: t.List[str] = [
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
    PANELS: t.List[str] = []
    DISABLE_PANELS: t.Sequence[str] = [
        "debug_toolbar.panels.redirects.RedirectsPanel",
    ]
    ALLOWED_IPS: t.Optional[t.Sequence[IPvAnyAddress]] = None
    JINJA_ENV: Environment = Environment()
    JINJA_LOADERS: t.List[BaseLoader] = []
    JINJA_EXTENSIONS: t.Sequence[t.Union[str, t.Type[Extension]]] = []
    API_URL: str = "/_debug_toolbar"
    STATIC_URL: str = f"{API_URL}/static"
    SHOW_TOOLBAR_CALLBACK: str = "debug_toolbar.middleware.show_toolbar"
    INSERT_BEFORE: str = "</body>"
    SHOW_COLLAPSE: bool = False
    ROOT_TAG_EXTRA_ATTRS: str = ""
    RESULTS_CACHE_SIZE: int = 25
    PROFILER_OPTIONS: t.Dict[str, t.Any] = {"interval": 0.0001}
    SETTINGS: t.Sequence[BaseSettings] = []
    LOGGING_COLORS: t.Dict[str, Color] = {
        "CRITICAL": Color("rgba(255, 0, 0, .4)"),
        "ERROR": Color("rgba(255, 0, 0, .2)"),
        "WARNING": Color("rgba(255, 165, 0, .2)"),
        "INFO": Color("rgba(135, 206, 235, .2)"),
        "DEBUG": Color("rgba(128, 128, 128, .2)"),
    }

    class Config:
        title = "Debug Toolbar"
        env_prefix = "DT_"
        case_sensitive = True

    def __init__(self, **settings: t.Any) -> None:
        super().__init__(**settings)
        loaders = self.JINJA_LOADERS + [PackageLoader("debug_toolbar", "templates")]
        self.JINJA_ENV.loader = ChoiceLoader(loaders)
        for extension in self.JINJA_EXTENSIONS:
            self.JINJA_ENV.add_extension(extension)

    @root_validator(pre=True)
    def ci(cls, values: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
        return {k.upper(): v for k, v in values.items()}
