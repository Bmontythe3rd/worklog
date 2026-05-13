import threading
import customtkinter as ctk
from datetime import date
import database
import ai_summary


class SummaryDialog(ctk.CTkToplevel):
    def __init__(self, parent, entries, mode="period", start_date=None, end_date=None):
        super().__init__(parent)
        self._mode = mode
        self._entries = entries
        self._streaming = False

        title = "Annual Review Generator" if mode == "annual" else "Period Summary"
        self.title(title)
        self.geometry("820x680")
        self.transient(parent)
        self.grab_set()

        self._build_ui(start_date, end_date)

    def _build_ui(self, start_date, end_date):
        outer = ctk.CTkFrame(self, fg_color="transparent")
        outer.pack(fill="both", expand=True, padx=20, pady=15)

        # Header
        header_text = "Annual Review Generator" if self._mode == "annual" else "Period Summary"
        ctk.CTkLabel(outer, text=header_text, font=ctk.CTkFont(size=18, weight="bold"), anchor="w").pack(fill="x", pady=(0, 12))

        # Controls row
        ctrl = ctk.CTkFrame(outer, fg_color="transparent")
        ctrl.pack(fill="x", pady=(0, 10))

        if self._mode == "annual":
            ctk.CTkLabel(ctrl, text="Year:", width=40).pack(side="left")
            self._year_var = ctk.StringVar(value=str(date.today().year))
            ctk.CTkEntry(ctrl, textvariable=self._year_var, width=80).pack(side="left", padx=(4, 15))
        else:
            ctk.CTkLabel(ctrl, text="From:").pack(side="left")
            self._from_var = ctk.StringVar(value=start_date or "")
            ctk.CTkEntry(ctrl, textvariable=self._from_var, placeholder_text="YYYY-MM-DD", width=120).pack(side="left", padx=(4, 12))
            ctk.CTkLabel(ctrl, text="To:").pack(side="left")
            self._to_var = ctk.StringVar(value=end_date or "")
            ctk.CTkEntry(ctrl, textvariable=self._to_var, placeholder_text="YYYY-MM-DD", width=120).pack(side="left", padx=(4, 0))

        self._gen_btn = ctk.CTkButton(ctrl, text="Generate", width=100, command=self._start_generation)
        self._gen_btn.pack(side="right")

        # Status label
        self._status = ctk.CTkLabel(outer, text="", text_color=("gray50", "gray60"), anchor="w", font=ctk.CTkFont(size=12))
        self._status.pack(fill="x", pady=(0, 5))

        # Output text area
        self._output = ctk.CTkTextbox(outer, wrap="word", font=ctk.CTkFont(size=13))
        self._output.pack(fill="both", expand=True, pady=(0, 12))
        self._output.configure(state="disabled")

        # Bottom buttons
        btn_row = ctk.CTkFrame(outer, fg_color="transparent")
        btn_row.pack(fill="x")
        ctk.CTkButton(btn_row, text="Close", fg_color="transparent", border_width=2, width=90, command=self.destroy).pack(side="right", padx=(8, 0))
        ctk.CTkButton(btn_row, text="Copy", width=90, command=self._copy).pack(side="right")
        ctk.CTkButton(btn_row, text="Clear", width=90, fg_color="transparent", border_width=2, command=self._clear).pack(side="left")

    def _start_generation(self):
        if self._streaming:
            return

        self._clear()

        if self._mode == "annual":
            try:
                year = int(self._year_var.get().strip())
            except ValueError:
                self._set_status("Please enter a valid year.")
                return
            start = f"{year}-01-01"
            end = f"{year}-12-31"
            entries = database.get_all_entries(start, end)
            if not entries:
                self._set_status(f"No entries found for {year}.")
                return
            generator = lambda: ai_summary.stream_annual_review(entries, year)
        else:
            start = self._from_var.get().strip() or None
            end = self._to_var.get().strip() or None
            entries = database.get_all_entries(start, end)
            if not entries:
                self._set_status("No entries found for the selected period.")
                return
            generator = lambda: ai_summary.stream_period_summary(entries, start or "start", end or "today")

        self._set_status(f"Generating summary for {len(entries)} entries...")
        self._gen_btn.configure(state="disabled")
        self._streaming = True

        thread = threading.Thread(target=self._run_stream, args=(generator,), daemon=True)
        thread.start()

    def _run_stream(self, generator):
        try:
            for chunk in generator():
                self.after(0, self._append, chunk)
            self.after(0, self._on_done)
        except Exception as exc:
            self.after(0, self._on_error, str(exc))

    def _append(self, text: str):
        self._output.configure(state="normal")
        self._output.insert("end", text)
        self._output.see("end")
        self._output.configure(state="disabled")

    def _on_done(self):
        self._streaming = False
        self._set_status("Done.")
        self._gen_btn.configure(state="normal")

    def _on_error(self, msg: str):
        self._streaming = False
        self._append(f"\n\n[Error: {msg}]")
        self._set_status("Error — see output above.")
        self._gen_btn.configure(state="normal")

    def _set_status(self, text: str):
        self._status.configure(text=text)

    def _clear(self):
        self._output.configure(state="normal")
        self._output.delete("1.0", "end")
        self._output.configure(state="disabled")
        self._set_status("")

    def _copy(self):
        content = self._output.get("1.0", "end").strip()
        if content:
            self.clipboard_clear()
            self.clipboard_append(content)
            self._set_status("Copied to clipboard.")
