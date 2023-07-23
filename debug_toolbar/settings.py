import typing as t

from jinja2 import BaseLoader, ChoiceLoader, Environment, PackageLoader
from jinja2.ext import Extension
from pydantic import Field, IPvAnyAddress, model_validator
from pydantic_extra_types.color import Color
from pydantic_settings import BaseSettings, SettingsConfigDict


class DebugToolbarSettings(BaseSettings):
    model_config = SettingsConfigDict(
        title="Debug Toolbar",
        env_prefix="DT_",
        case_sensitive=False,
    )

    DEFAULT_PANELS: t.List[str] = Field(
        [
            "debug_toolbar.panels.versions.VersionsPanel",
            "debug_toolbar.panels.timer.TimerPanel",
            "debug_toolbar.panels.settings.SettingsPanel",
            "debug_toolbar.panels.request.RequestPanel",
            "debug_toolbar.panels.headers.HeadersPanel",
            "debug_toolbar.panels.routes.RoutesPanel",
            "debug_toolbar.panels.logging.LoggingPanel",
            "debug_toolbar.panels.profiling.ProfilingPanel",
            "debug_toolbar.panels.redirects.RedirectsPanel",
        ],
        description=(
            "Specifies the full Python path to each panel that you "
            "want included in the toolbar."
        ),
    )
    PANELS: t.List[str] = Field(
        [],
        description=(
            "A list of the full Python paths to each panel that you "
            "want to append to `DEFAULT_PANELS`."
        ),
    )
    DISABLE_PANELS: t.Sequence[str] = Field(
        ["debug_toolbar.panels.redirects.RedirectsPanel"],
        description=(
            "A list of the full Python paths to each panel that you "
            "want disabled (but still displayed) by default."
        ),
    )
    ALLOWED_IPS: t.Optional[t.Sequence[IPvAnyAddress]] = Field(
        None,
        description=(
            "If it's set, the Debug Toolbar is shown only "
            "if your IP address is listed."
        ),
    )
    JINJA_ENV: Environment = Field(
        Environment(),
        description="The Jinja environment instance used to render the toolbar.",
    )
    JINJA_LOADERS: t.List[BaseLoader] = Field(
        [],
        description=(
            "Jinja `BaseLoader` subclasses used to load templates "
            "from the file system or other locations."
        ),
    )
    JINJA_EXTENSIONS: t.Sequence[t.Union[str, t.Type[Extension]]] = Field(
        [],
        description=(
            "Load the extensions from the list and bind them to the Jinja environment."
        ),
    )
    API_URL: str = Field(
        "/_debug_toolbar",
        description="URL prefix to use for toolbar endpoints.",
    )
    STATIC_URL: str = Field(
        f"{API_URL.default}/static",  # type: ignore[attr-defined]
        description="URL to use when referring to toolbar static files.",
    )
    SHOW_TOOLBAR_CALLBACK: str = Field(
        "debug_toolbar.middleware.show_toolbar",
        description=(
            "This is the dotted path to a function used for "
            "determining whether the toolbar should show or not."
        ),
    )
    INSERT_BEFORE: str = Field(
        "</body>",
        description=(
            "The toolbar searches for this string in the HTML "
            "and inserts itself just before."
        ),
    )
    SHOW_COLLAPSE: bool = Field(
        False,
        description="If changed to `True`, the toolbar will be collapsed by default.",
    )
    ROOT_TAG_EXTRA_ATTRS: str = Field(
        "",
        description=(
            "This setting is injected in the root template div "
            "in order to avoid conflicts with client-side frameworks"
        ),
    )
    RESULTS_CACHE_SIZE: int = Field(
        25,
        description="The toolbar keeps up to this many results in memory.",
    )
    PROFILER_OPTIONS: t.Dict[str, t.Any] = Field(
        {"interval": 0.0001},
        description="A list of arguments can be supplied to the Profiler.",
    )
    SETTINGS: t.Sequence[BaseSettings] = Field(
        [],
        description=(
            "pydantic's `BaseSettings` instances to be "
            "displayed on the `SettingsPanel`."
        ),
    )
    LOGGING_COLORS: t.Dict[str, Color] = Field(
        {
            "CRITICAL": Color("rgba(255, 0, 0, .4)"),
            "ERROR": Color("rgba(255, 0, 0, .2)"),
            "WARNING": Color("rgba(255, 165, 0, .2)"),
            "INFO": Color("rgba(135, 206, 235, .2)"),
            "DEBUG": Color("rgba(128, 128, 128, .2)"),
        },
        description="Color palette used to apply colors based on the log level.",
    )
    SQL_WARNING_THRESHOLD: int = Field(
        500,
        description=(
            "The SQL panel highlights queries that took more that this amount of "
            "time, in milliseconds, to execute."
        ),
    )

    def __init__(self, **settings: t.Any) -> None:
        super().__init__(**settings)
        loaders = self.JINJA_LOADERS + [PackageLoader("debug_toolbar", "templates")]
        self.JINJA_ENV.loader = ChoiceLoader(loaders)
        self.JINJA_ENV.trim_blocks = True
        self.JINJA_ENV.lstrip_blocks = True

        for extension in self.JINJA_EXTENSIONS:
            self.JINJA_ENV.add_extension(extension)

    @model_validator(mode="before")
    def ci(cls, data: dict):
        return {k.upper(): v for k, v in data.items()}
