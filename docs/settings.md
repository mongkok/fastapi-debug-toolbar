Here's a list of settings available:

::: debug_toolbar.settings.DebugToolbarSettings
    handlers: python
    rendering:
      show_root_heading: false
      show_root_toc_entry: false
      show_root_full_path: false
      show_if_no_docstring: true
      heading_level: 3
    selection:
      filters:
        - "!^_"
        - "!Config$"
        - "!ci$"
    watch:
      - debug_toolbar/settings.py
