from tkinter import messagebox
import customtkinter as ctk
from datetime import datetime
import database
from ui import entry_form, summary_dialog

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

_ROW_DEFAULT = ("gray17", "gray17")
_ROW_HOVER = ("gray22", "gray22")
_ROW_SELECTED = ("gray28", "gray28")


def _bind_tree(widget, event, callback):
    widget.bind(event, callback)
    for child in widget.winfo_children():
        _bind_tree(child, event, callback)


class EntryRow(ctk.CTkFrame):
    def __init__(self, parent, entry, on_click):
        super().__init__(parent, corner_radius=8, cursor="hand2", fg_color=_ROW_DEFAULT)
        self._entry_id = entry["id"]
        self._selected = False

        try:
            d = datetime.strptime(entry["date"], "%Y-%m-%d")
            date_str = d.strftime("%b %d")
        except ValueError:
            date_str = entry["date"]

        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="x", padx=10, pady=8)

        top = ctk.CTkFrame(inner, fg_color="transparent")
        top.pack(fill="x")

        ctk.CTkLabel(
            top, text=date_str, font=ctk.CTkFont(size=11),
            text_color=("gray60", "gray55"), width=48, anchor="w",
        ).pack(side="left")

        title = entry["title"][:44] + ("…" if len(entry["title"]) > 44 else "")
        ctk.CTkLabel(
            top, text=title, font=ctk.CTkFont(size=12, weight="bold"), anchor="w",
        ).pack(side="left", fill="x", expand=True)

        tags = " · ".join(filter(None, [entry["project"] or "", entry["category"] or ""]))
        if tags:
            ctk.CTkLabel(
                inner, text=tags, font=ctk.CTkFont(size=10),
                text_color=("gray60", "gray55"), anchor="w",
            ).pack(fill="x", padx=48)

        _bind_tree(self, "<Button-1>", lambda e, eid=self._entry_id: on_click(eid))
        _bind_tree(self, "<Enter>", lambda e: self._hover(True))
        _bind_tree(self, "<Leave>", lambda e: self._hover(False))

    def set_selected(self, selected: bool):
        self._selected = selected
        if selected:
            self.configure(fg_color=_ROW_SELECTED)
        else:
            self.configure(fg_color=_ROW_DEFAULT)

    def _hover(self, entering: bool):
        if not self._selected:
            self.configure(fg_color=_ROW_HOVER if entering else _ROW_DEFAULT)


class WorklogApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Worklog")
        self.geometry("1200x760")
        self.minsize(900, 600)

        self._selected_id = None
        self._rows: list[tuple[int, EntryRow]] = []

        self._build_ui()
        database.init_db()
        self._load_entries()

    # ── UI construction ─────────────────────────────────────────────────────

    def _build_ui(self):
        self._build_topbar()
        content = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        content.pack(fill="both", expand=True)
        self._build_left(content)
        ctk.CTkFrame(content, width=1, fg_color=("gray30", "gray25")).pack(side="left", fill="y")
        self._build_right(content)

    def _build_topbar(self):
        bar = ctk.CTkFrame(self, height=58, corner_radius=0, fg_color=("gray90", "gray13"))
        bar.pack(fill="x", side="top")
        bar.pack_propagate(False)

        ctk.CTkLabel(bar, text="Worklog", font=ctk.CTkFont(size=20, weight="bold")).pack(side="left", padx=20)

        right = ctk.CTkFrame(bar, fg_color="transparent")
        right.pack(side="right", padx=15)

        ctk.CTkButton(right, text="+ New Entry", width=115, command=self._new_entry).pack(side="right", padx=4)
        ctk.CTkButton(right, text="Annual Review", width=125, fg_color="transparent", border_width=2, command=self._annual_review).pack(side="right", padx=4)
        ctk.CTkButton(right, text="Summarize Period", width=140, fg_color="transparent", border_width=2, command=self._summarize_period).pack(side="right", padx=4)

    def _build_left(self, parent):
        panel = ctk.CTkFrame(parent, width=330, corner_radius=0, fg_color=("gray93", "gray14"))
        panel.pack(side="left", fill="y")
        panel.pack_propagate(False)

        # Filters
        f = ctk.CTkFrame(panel, fg_color="transparent")
        f.pack(fill="x", padx=12, pady=(12, 4))

        ctk.CTkLabel(f, text="Filter", font=ctk.CTkFont(weight="bold"), anchor="w").pack(fill="x")

        row1 = ctk.CTkFrame(f, fg_color="transparent")
        row1.pack(fill="x", pady=(5, 2))
        ctk.CTkLabel(row1, text="From:", width=42, anchor="w").pack(side="left")
        self._f_from = ctk.CTkEntry(row1, placeholder_text="YYYY-MM-DD", width=140)
        self._f_from.pack(side="left")

        row2 = ctk.CTkFrame(f, fg_color="transparent")
        row2.pack(fill="x", pady=2)
        ctk.CTkLabel(row2, text="To:", width=42, anchor="w").pack(side="left")
        self._f_to = ctk.CTkEntry(row2, placeholder_text="YYYY-MM-DD", width=140)
        self._f_to.pack(side="left")

        row3 = ctk.CTkFrame(f, fg_color="transparent")
        row3.pack(fill="x", pady=2)
        ctk.CTkLabel(row3, text="Project:", width=55, anchor="w").pack(side="left")
        self._f_project = ctk.CTkComboBox(row3, values=["All"], width=170, command=self._load_entries)
        self._f_project.set("All")
        self._f_project.pack(side="left")

        btns = ctk.CTkFrame(f, fg_color="transparent")
        btns.pack(fill="x", pady=(6, 0))
        ctk.CTkButton(btns, text="Apply", width=75, height=28, command=self._load_entries).pack(side="left")
        ctk.CTkButton(btns, text="Clear", width=65, height=28, fg_color="transparent", border_width=1, command=self._clear_filter).pack(side="left", padx=6)

        ctk.CTkFrame(panel, height=1, fg_color=("gray75", "gray28")).pack(fill="x", padx=10, pady=6)

        self._count_lbl = ctk.CTkLabel(panel, text="", text_color=("gray50", "gray55"), font=ctk.CTkFont(size=11), anchor="w")
        self._count_lbl.pack(fill="x", padx=14, pady=(0, 4))

        self._list_frame = ctk.CTkScrollableFrame(panel, fg_color="transparent")
        self._list_frame.pack(fill="both", expand=True, padx=6, pady=(0, 6))

    def _build_right(self, parent):
        panel = ctk.CTkFrame(parent, corner_radius=0, fg_color="transparent")
        panel.pack(side="left", fill="both", expand=True)

        # Placeholder
        self._placeholder = ctk.CTkFrame(panel, fg_color="transparent")
        self._placeholder.pack(fill="both", expand=True)
        ctk.CTkLabel(
            self._placeholder,
            text="Select an entry to view details\nor click + New Entry to get started",
            text_color=("gray55", "gray55"),
            font=ctk.CTkFont(size=15),
            justify="center",
        ).pack(expand=True)

        # Detail view
        self._detail = ctk.CTkFrame(panel, fg_color="transparent")

        hdr = ctk.CTkFrame(self._detail, fg_color="transparent")
        hdr.pack(fill="x", padx=25, pady=(22, 0))

        self._d_title = ctk.CTkLabel(hdr, text="", font=ctk.CTkFont(size=21, weight="bold"), anchor="w", wraplength=700)
        self._d_title.pack(fill="x")

        meta = ctk.CTkFrame(self._detail, fg_color="transparent")
        meta.pack(fill="x", padx=25, pady=(6, 0))

        self._d_date = ctk.CTkLabel(meta, text="", text_color=("gray50", "gray60"), font=ctk.CTkFont(size=12))
        self._d_date.pack(side="left")
        self._d_project = ctk.CTkLabel(meta, text="", text_color=("gray50", "gray60"), font=ctk.CTkFont(size=12))
        self._d_project.pack(side="left", padx=(14, 0))
        self._d_category = ctk.CTkLabel(meta, text="", text_color=("gray50", "gray60"), font=ctk.CTkFont(size=12))
        self._d_category.pack(side="left", padx=(14, 0))

        ctk.CTkFrame(self._detail, height=1, fg_color=("gray75", "gray28")).pack(fill="x", padx=25, pady=14)

        ctk.CTkLabel(self._detail, text="Notes", font=ctk.CTkFont(weight="bold"), anchor="w").pack(fill="x", padx=25)

        self._d_desc = ctk.CTkTextbox(self._detail, wrap="word", font=ctk.CTkFont(size=13), state="disabled")
        self._d_desc.pack(fill="both", expand=True, padx=25, pady=(6, 10))

        action_bar = ctk.CTkFrame(self._detail, fg_color="transparent")
        action_bar.pack(fill="x", padx=25, pady=(0, 18))
        ctk.CTkButton(action_bar, text="Edit Entry", width=100, command=self._edit_entry).pack(side="left")
        ctk.CTkButton(
            action_bar, text="Delete", width=90,
            fg_color="#8b2020", hover_color="#a83232",
            command=self._delete_entry,
        ).pack(side="left", padx=10)

    # ── Entry list ───────────────────────────────────────────────────────────

    def _load_entries(self, *_):
        from_date = self._f_from.get().strip() or None
        to_date = self._f_to.get().strip() or None
        project = self._f_project.get()
        project = None if project == "All" else project

        entries = database.get_all_entries(from_date, to_date, project)

        for _, row in self._rows:
            row.destroy()
        self._rows.clear()

        self._count_lbl.configure(text=f"{len(entries)} {'entry' if len(entries) == 1 else 'entries'}")

        for e in entries:
            row = EntryRow(self._list_frame, e, self._select_entry)
            row.pack(fill="x", pady=2)
            self._rows.append((e["id"], row))

        projects = ["All"] + database.get_projects()
        current = self._f_project.get()
        self._f_project.configure(values=projects)
        self._f_project.set(current if current in projects else "All")

        if self._selected_id and not any(eid == self._selected_id for eid, _ in self._rows):
            self._selected_id = None
            self._detail.pack_forget()
            self._placeholder.pack(fill="both", expand=True)

    def _select_entry(self, entry_id: int):
        self._selected_id = entry_id

        for eid, row in self._rows:
            row.set_selected(eid == entry_id)

        entry = database.get_entry(entry_id)
        if not entry:
            return

        self._placeholder.pack_forget()
        self._detail.pack(fill="both", expand=True)

        self._d_title.configure(text=entry["title"])
        self._d_date.configure(text=entry["date"])
        self._d_project.configure(text=f"[{entry['project']}]" if entry["project"] else "")
        self._d_category.configure(text=entry["category"] if entry["category"] else "")

        self._d_desc.configure(state="normal")
        self._d_desc.delete("1.0", "end")
        self._d_desc.insert("1.0", entry["description"] or "")
        self._d_desc.configure(state="disabled")

    # ── Actions ──────────────────────────────────────────────────────────────

    def _new_entry(self):
        dlg = entry_form.EntryForm(self, title="New Entry")
        self.wait_window(dlg)
        self._load_entries()

    def _edit_entry(self):
        if not self._selected_id:
            return
        entry = database.get_entry(self._selected_id)
        dlg = entry_form.EntryForm(self, title="Edit Entry", entry=entry)
        self.wait_window(dlg)
        self._load_entries()
        if self._selected_id:
            self._select_entry(self._selected_id)

    def _delete_entry(self):
        if not self._selected_id:
            return
        if messagebox.askyesno("Delete Entry", "Delete this entry? This cannot be undone.", parent=self):
            database.delete_entry(self._selected_id)
            self._selected_id = None
            self._detail.pack_forget()
            self._placeholder.pack(fill="both", expand=True)
            self._load_entries()

    def _summarize_period(self):
        from_date = self._f_from.get().strip() or None
        to_date = self._f_to.get().strip() or None
        entries = database.get_all_entries(from_date, to_date)
        if not entries:
            messagebox.showinfo("No Entries", "No entries found for the selected period.", parent=self)
            return
        dlg = summary_dialog.SummaryDialog(self, entries=entries, mode="period", start_date=from_date, end_date=to_date)
        self.wait_window(dlg)

    def _annual_review(self):
        dlg = summary_dialog.SummaryDialog(self, entries=None, mode="annual")
        self.wait_window(dlg)

    def _clear_filter(self):
        self._f_from.delete(0, "end")
        self._f_to.delete(0, "end")
        self._f_project.set("All")
        self._load_entries()
