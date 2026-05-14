#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Ensure the project root is on the path so relative imports work when
# the script is invoked from any directory.
sys.path.insert(0, str(Path(__file__).parent))

import customtkinter as ctk
import config
import database
from ui.app import WorklogApp


def _apply_hidpi_scaling():
    scale = float(os.environ.get("GDK_SCALE", 1))
    if scale > 1:
        ctk.set_widget_scaling(scale)
        ctk.set_window_scaling(scale)


def _load_api_key():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        stored = config.get_api_key()
        if stored:
            os.environ["ANTHROPIC_API_KEY"] = stored


def main():
    _apply_hidpi_scaling()
    _load_api_key()

    database.init_db()
    app = WorklogApp()
    app.mainloop()


if __name__ == "__main__":
    main()
