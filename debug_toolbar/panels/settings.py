from debug_toolbar.panels import Panel


class SettingsPanel(Panel):
    title = "Settings"
    template = "panels/settings.html"
