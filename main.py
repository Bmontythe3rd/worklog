#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Ensure the project root is on the path so relative imports work when
# the script is invoked from any directory.
sys.path.insert(0, str(Path(__file__).parent))

import database
from ui.app import WorklogApp


def main():
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
