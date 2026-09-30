"""Desktop batch importer for Fortcamp generic portrait contact sheets."""
from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from portrait_import_core import (
    POOL_PATTERN, import_sheet, is_imported, pixel_digest, pool_count,
    read_manifest, refresh_entry, refresh_sheet,
)

ROOT = Path(__file__).resolve().parents[1]
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}


class PortraitPoolImporter(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Fortcamp Portrait Pool Importer")
        self.geometry("1040x680")
        self.minsize(850, 540)
        self.folder = ROOT / "portraits"
        self.rows_by_id: dict[str, dict] = {}
        self.folder_value = tk.StringVar(value=str(self.folder))
        self.status_value = tk.StringVar(value="Choose a folder or import the safe new pools.")
        self._build()
        self.scan()

    def _build(self) -> None:
        shell = ttk.Frame(self, padding=14)
        shell.pack(fill="both", expand=True)
        shell.columnconfigure(0, weight=1)
        shell.rowconfigure(2, weight=1)
        ttk.Label(shell, text="Fortcamp Portrait Pool Importer", font=("Segoe UI", 18, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(shell, text="5×4 sheets: Import adds new IDs; Repair rebuilds the same existing IDs from their source sheet.").grid(row=1, column=0, sticky="w", pady=(2, 10))

        self.tree = ttk.Treeview(shell, columns=("pool", "existing", "status"), show="headings", selectmode="extended")
        self.tree.heading("pool", text="Portrait pool")
        self.tree.heading("existing", text="Existing portraits")
        self.tree.heading("status", text="Import status")
        self.tree.column("pool", width=330)
        self.tree.column("existing", width=130, anchor="center")
        self.tree.column("status", width=360)
        scroll = ttk.Scrollbar(shell, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.grid(row=2, column=0, sticky="nsew")
        scroll.grid(row=2, column=1, sticky="ns")

        controls = ttk.Frame(shell)
        controls.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        controls.columnconfigure(1, weight=1)
        ttk.Button(controls, text="Choose Folder", command=self.choose_folder).grid(row=0, column=0, padx=(0, 8))
        ttk.Entry(controls, textvariable=self.folder_value, state="readonly").grid(row=0, column=1, sticky="ew")
        ttk.Button(controls, text="Refresh", command=self.scan).grid(row=0, column=2, padx=(8, 0))
        ttk.Button(controls, text="Import New Pools", command=self.import_safe).grid(row=1, column=0, pady=(10, 0), sticky="ew")
        ttk.Button(controls, text="Add Selected as New Portraits", command=self.append_selected).grid(row=1, column=1, pady=(10, 0), padx=8, sticky="w")
        ttk.Button(controls, text="Repair Selected Existing IDs", command=self.repair_selected).grid(row=1, column=2, pady=(10, 0), sticky="ew")
        ttk.Label(controls, textvariable=self.status_value).grid(row=2, column=0, columnspan=3, sticky="w", pady=(10, 0))

    def choose_folder(self) -> None:
        selected = filedialog.askdirectory(initialdir=self.folder, title="Choose folder containing contact sheets")
        if selected:
            self.folder = Path(selected)
            self.folder_value.set(str(self.folder))
            self.scan()

    def scan(self) -> None:
        self.tree.delete(*self.tree.get_children())
        self.rows_by_id.clear()
        manifest = read_manifest()
        invalid = 0
        paths = sorted(self.folder.iterdir(), key=lambda item: item.name.casefold()) if self.folder.is_dir() else []
        for path in paths:
            if not path.is_file() or path.suffix.lower() not in IMAGE_SUFFIXES:
                continue
            pool = path.stem.lower()
            if not POOL_PATTERN.fullmatch(pool):
                invalid += 1
                continue
            try:
                digest = pixel_digest(path)
                existing = pool_count(pool)
                duplicate = is_imported(pool, digest, manifest)
                repair = refresh_entry(path, pool, manifest)
                if duplicate:
                    status, state = "Previously imported — Repair rebuilds the same IDs", "duplicate"
                elif existing == 0:
                    status, state = "Ready — empty/new pool", "safe"
                elif repair:
                    status, state = "Edited source — Repair updates its existing IDs", "revision"
                else:
                    status, state = "Existing pool — Add creates 20 new IDs", "revision"
            except Exception as exc:
                existing, digest, repair, state, status = 0, "", None, "error", f"Error: {exc}"
            item = self.tree.insert("", "end", values=(pool, existing, status))
            self.rows_by_id[item] = {"path": path, "pool": pool, "digest": digest, "state": state, "repair": repair}
            if state == "safe":
                self.tree.selection_add(item)
        suffix = f"; ignored {invalid} noncanonical/versioned filename(s)" if invalid else ""
        self.status_value.set(f"Found {len(self.rows_by_id)} eligible sheet(s){suffix}.")

    def _import_rows(self, rows: list[dict]) -> None:
        imported = skipped = tagged = 0
        failures: list[str] = []
        for row in rows:
            try:
                result = import_sheet(row["path"], row["pool"])
                if result["status"] == "duplicate":
                    skipped += 1
                else:
                    imported += len(result["written"])
                    tagged += int(result.get("metadata_written", 0))
            except Exception as exc:
                failures.append(f"{row['path'].name}: {exc}")
        self.scan()
        self.status_value.set(f"Imported {imported} portrait(s), attached {tagged} appearance record(s); skipped {skipped} duplicate sheet(s).")
        if failures:
            messagebox.showerror("Some imports failed", "\n".join(failures[:12]))

    def import_safe(self) -> None:
        rows = [row for row in self.rows_by_id.values() if row["state"] == "safe"]
        if not rows:
            messagebox.showinfo("Nothing to import", "There are no unimported sheets targeting empty pools.")
            return
        self._import_rows(rows)

    def append_selected(self) -> None:
        rows = [self.rows_by_id[item] for item in self.tree.selection() if self.rows_by_id[item]["state"] not in {"error", "duplicate"}]
        if not rows:
            messagebox.showinfo("Nothing selected", "Select one or more new or revised sheets.")
            return
        revisions = sum(row["state"] == "revision" for row in rows)
        if revisions and not messagebox.askyesno("Append revisions?", f"{revisions} selected sheet(s) target existing pools. Their portraits will be appended; existing IDs remain unchanged. Continue?"):
            return
        self._import_rows(rows)

    def repair_selected(self) -> None:
        rows = [self.rows_by_id[item] for item in self.tree.selection() if self.rows_by_id[item].get("repair")]
        if not rows:
            messagebox.showinfo(
                "Nothing repairable selected",
                "Select a sheet marked 'Previously imported' or 'Edited source'. Repair keeps its existing portrait IDs.",
            )
            return
        pools = "\n".join(f"• {row['pool']}" for row in rows)
        if not messagebox.askyesno(
            "Repair existing portrait IDs?",
            f"These pools will be rebuilt from their 5×4 sheets:\n\n{pools}\n\nCurrent full images and thumbnails will be backed up first.",
        ):
            return
        repaired: list[str] = []
        failures: list[str] = []
        for row in rows:
            try:
                result = refresh_sheet(row["path"], row["pool"])
                repaired.append(f"{row['pool']} ({len(result['files'])} IDs)")
            except Exception as exc:
                failures.append(f"{row['path'].name}: {exc}")
        self.scan()
        self.status_value.set(f"Repaired {len(repaired)} pool(s) without changing portrait IDs.")
        if repaired:
            messagebox.showinfo("Repair complete", "Repaired:\n" + "\n".join(repaired))
        if failures:
            messagebox.showerror("Some repairs failed", "\n".join(failures[:12]))


if __name__ == "__main__":
    PortraitPoolImporter().mainloop()
