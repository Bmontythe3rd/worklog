import customtkinter as ctk
from datetime import date
import database


class EntryForm(ctk.CTkToplevel):
    def __init__(self, parent, title="New Entry", entry=None):
        super().__init__(parent)
        self.entry = entry
        self.title(title)
        self.geometry("560x560")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._build_ui()
        if entry:
            self._populate(entry)
        else:
            self.date_var.set(date.today().strftime("%Y-%m-%d"))

        self.after(100, self.title_entry.focus_set)

    def _build_ui(self):
        outer = ctk.CTkFrame(self, fg_color="transparent")
        outer.pack(fill="both", expand=True, padx=25, pady=20)

        ctk.CTkLabel(outer, text="Date", font=ctk.CTkFont(weight="bold"), anchor="w").pack(fill="x")
        self.date_var = ctk.StringVar()
        ctk.CTkEntry(outer, textvariable=self.date_var, placeholder_text="YYYY-MM-DD").pack(fill="x", pady=(3, 12))

        ctk.CTkLabel(outer, text="Title *", font=ctk.CTkFont(weight="bold"), anchor="w").pack(fill="x")
        self.title_entry = ctk.CTkEntry(outer, placeholder_text="What did you work on?")
        self.title_entry.pack(fill="x", pady=(3, 12))

        row = ctk.CTkFrame(outer, fg_color="transparent")
        row.pack(fill="x", pady=(0, 12))
        row.columnconfigure(0, weight=1)
        row.columnconfigure(1, weight=1)

        proj_col = ctk.CTkFrame(row, fg_color="transparent")
        proj_col.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        ctk.CTkLabel(proj_col, text="Project", font=ctk.CTkFont(weight="bold"), anchor="w").pack(fill="x")
        projects = [""] + database.get_projects()
        self.project_var = ctk.StringVar()
        self.project_combo = ctk.CTkComboBox(proj_col, variable=self.project_var, values=projects)
        self.project_combo.pack(fill="x", pady=(3, 0))

        cat_col = ctk.CTkFrame(row, fg_color="transparent")
        cat_col.grid(row=0, column=1, sticky="ew")
        ctk.CTkLabel(cat_col, text="Category", font=ctk.CTkFont(weight="bold"), anchor="w").pack(fill="x")
        self.category_var = ctk.StringVar()
        self.category_combo = ctk.CTkComboBox(
            cat_col,
            variable=self.category_var,
            values=[""] + database.PRESET_CATEGORIES,
        )
        self.category_combo.pack(fill="x", pady=(3, 0))

        ctk.CTkLabel(outer, text="Notes", font=ctk.CTkFont(weight="bold"), anchor="w").pack(fill="x")
        self.desc_text = ctk.CTkTextbox(outer, height=160, wrap="word")
        self.desc_text.pack(fill="both", expand=True, pady=(3, 15))

        self.error_label = ctk.CTkLabel(outer, text="", text_color="#e74c3c", anchor="w")
        self.error_label.pack(fill="x")

        btn_row = ctk.CTkFrame(outer, fg_color="transparent")
        btn_row.pack(fill="x", pady=(5, 0))
        ctk.CTkButton(btn_row, text="Cancel", fg_color="transparent", border_width=2, width=100, command=self.destroy).pack(side="right", padx=(8, 0))
        label = "Save Changes" if self.entry else "Add Entry"
        ctk.CTkButton(btn_row, text=label, width=120, command=self._save).pack(side="right")

    def _populate(self, entry):
        self.date_var.set(entry["date"])
        self.title_entry.insert(0, entry["title"] or "")
        self.project_var.set(entry["project"] or "")
        self.category_var.set(entry["category"] or "")
        self.desc_text.insert("1.0", entry["description"] or "")

    def _save(self):
        date_val = self.date_var.get().strip()
        title_val = self.title_entry.get().strip()

        if not title_val:
            self.error_label.configure(text="Title is required.")
            return
        if not date_val:
            self.error_label.configure(text="Date is required.")
            return

        desc = self.desc_text.get("1.0", "end").strip()
        project = self.project_var.get().strip()
        category = self.category_var.get().strip()

        if self.entry:
            database.update_entry(self.entry["id"], date_val, title_val, desc, project, category)
        else:
            database.create_entry(date_val, title_val, desc, project, category)

        self.destroy()
