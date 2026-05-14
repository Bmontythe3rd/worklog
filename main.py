#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Ensure the project root is on the path so relative imports work when
# the script is invoked from any directory.
sys.path.insert(0, str(Path(__file__).parent))

import customtkinter as ctk
import database
from ui.app import WorklogApp


def _apply_hidpi_scaling():
    scale = float(os.environ.get("GDK_SCALE", 1))
    if scale > 1:
        ctk.set_widget_scaling(scale)
        ctk.set_window_scaling(scale)


def main():
    _apply_hidpi_scaling()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print(
            "Warning: ANTHROPIC_API_KEY is not set.\n"
            "The app will open, but AI summarization will not work until you set it:\n"
            "  export ANTHROPIC_API_KEY=sk-ant-...\n"
        )

    database.init_db()
    app = WorklogApp()
    app.mainloop()


if __name__ == "__main__":
    main()
