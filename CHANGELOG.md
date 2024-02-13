# Changelog

### 0.6.0

* **SQLAlchemyPanel**: Added `async_exit_stack` arg to `solve_dependencies` function 
* **DebugToolbarMiddleware**: Removed `settings.ALLOWED_IPS` in favor of `settings.ALLOWED_HOSTS`
* **VersionsPanel**: Removed `pkg_resources` in favor of `importlib.metadata`
* Added ruff and bandit and removed black and isort
* Removed deprecated `on_event`
* Added minor improvements

### 0.5.0

* Added Pydantic v2 support
* Removed Pydantic v1 support
* Removed `PydanticPanel`

### 0.4.0

* Fixed middleware `url_path_for`
* Improved SQLAlchemy panel

### 0.3.2

* Fixed response body stream

### 0.3.1

* Fixed pyproject.toml, added package data
* Improved panel templates
* Fixed profiling on Safari browser

### 0.3.0

* Added refresh cookie system and `JSON.parse` swap removed
* Fixed SQL query encoding
* Fixed `SQLAlchemyPanel` , added missing `fastapi_astack` to scope (`fastapi >= 0.74.0`)
* Added `SQLAlchemyPanel.add_engines` method
* Added `tortoise-orm >= 0.19.0` support
* Fixed `VersionsPanel` JS, package home can be null

### 0.2.1

* Added `PydanticPanel`
* Removed `current_thread` in favor of `get_ident`
* Added anyio task groups
* Removed `get_running_loop` in favor of `get_event_loop`
* Improved tables styles

### 0.2.0

* Fixed `ThreadPoolExecutor` for all sync endpoints
* Added cookie-based refresh
* Added exception handling for dependency resolution
* Added minor improvements to `VersionPanel`

### 0.1.3

* Added `TortoisePanel`

### 0.1.2

* Removed SQL compiled query in favor of statement params
* Added SQLAlchemy unregister
* Added `SQLPanel` base class

### 0.1.1

* Improved dependency resolution
* Added minor improvements

### 0.1.0

* Added `SQLAlchemyPanel`
* Added `LOGGING_COLORS` to panel templates
* Minor improvements

### 0.0.6

* Improved `VersionsPanel` script
* Added docs

### 0.0.5

* Fixed multiple profilers on the same thread
* Fixed `VersionsPanel` Pypi url

### 0.0.4

* Added pypi details to `VersionsPanel`
* Improved assets
* Added `LOGGING_COLORS`
* Highlighted matched endpoint

### 0.0.3

* Sorted routes by path

### 0.0.2

* Added mounted apps support (e.g. ariadne.asgi.GraphQL)

### 0.0.1

* 📦
