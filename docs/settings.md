Here's a list of settings available:

::: debug_toolbar.settings.DebugToolbarSettings
    handlers: python
    options:
      heading_level: 4
      show_bases: false
      show_if_no_docstring: true
      show_root_toc_entry: false
      filters:
        - "!^_"
        - "!Config$"
        - "!ci$"
    watch:
      - debug_toolbar/settings.py
