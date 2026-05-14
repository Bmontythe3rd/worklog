import os
import customtkinter as ctk
import config


class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.withdraw()
        self.title("Settings")
        self.geometry("480x320")
        self.resizable(False, False)
        self.transient(parent)

        self._build_ui()
        self.deiconify()
        self.grab_set()

    def _build_ui(self):
        outer = ctk.CTkFrame(self, fg_color="transparent")
        outer.pack(fill="both", expand=True, padx=30, pady=24)

        # Section header
        ctk.CTkLabel(
            outer, text="AI Integration",
            font=ctk.CTkFont(size=13, weight="bold"), anchor="w",
        ).pack(fill="x")
        ctk.CTkFrame(outer, height=1, fg_color=("gray75", "gray30")).pack(fill="x", pady=(4, 16))

        # API key label
        ctk.CTkLabel(
            outer, text="Anthropic API Key",
            font=ctk.CTkFont(size=12, weight="bold"), anchor="w",
        ).pack(fill="x")

        # Key entry row with Show/Hide toggle
        key_row = ctk.CTkFrame(outer, fg_color="transparent")
        key_row.pack(fill="x", pady=(4, 4))

        self._key_var = ctk.StringVar(value=config.get_api_key())
        self._key_entry = ctk.CTkEntry(
            key_row, textvariable=self._key_var,
            show="•", height=36, placeholder_text="sk-ant-...",
        )
        self._key_entry.pack(side="left", fill="x", expand=True)

        self._show_btn = ctk.CTkButton(
            key_row, text="Show", width=64, height=36,
            fg_color="transparent", border_width=1,
            command=self._toggle_show,
        )
        self._show_btn.pack(side="left", padx=(8, 0))

        ctk.CTkLabel(
            outer, text="Get your key at console.anthropic.com",
            font=ctk.CTkFont(size=11), text_color=("gray50", "gray55"), anchor="w",
        ).pack(fill="x", pady=(0, 16))

        # Status label
        self._status = ctk.CTkLabel(outer, text="", anchor="w", font=ctk.CTkFont(size=12))
        self._status.pack(fill="x")
        self._refresh_status()

        # Buttons
        btn_row = ctk.CTkFrame(outer, fg_color="transparent")
        btn_row.pack(fill="x", side="bottom")
        ctk.CTkButton(
            btn_row, text="Close", fg_color="transparent", border_width=2,
            width=100, height=36, command=self.destroy,
        ).pack(side="right", padx=(8, 0))
        ctk.CTkButton(
            btn_row, text="Save", width=100, height=36, command=self._save,
        ).pack(side="right")

    def _toggle_show(self):
        if self._key_entry.cget("show") == "•":
            self._key_entry.configure(show="")
            self._show_btn.configure(text="Hide")
        else:
            self._key_entry.configure(show="•")
            self._show_btn.configure(text="Show")

    def _refresh_status(self):
        stored = config.get_api_key()
        env = os.environ.get("ANTHROPIC_API_KEY", "")
        if stored or env:
            self._status.configure(text="✓ API key is configured", text_color="#4caf50")
        else:
            self._status.configure(text="No API key set — AI features will not work", text_color="#e57373")

    def _save(self):
        key = self._key_var.get().strip()
        config.set_api_key(key)
        if key:
            os.environ["ANTHROPIC_API_KEY"] = key
        elif "ANTHROPIC_API_KEY" in os.environ:
            del os.environ["ANTHROPIC_API_KEY"]
        self._refresh_status()
        self._status.configure(text="✓ Saved", text_color="#4caf50")
