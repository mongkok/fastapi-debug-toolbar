from debug_toolbar.panels import Panel


class SettingsPanel(Panel):
    title = "Debug Toolbar Settings"
    nav_title = "Settings"
    template = "panels/settings.html"
