"""Desktop UI for managing Fortcamp Champion portraits and expressions."""
from __future__ import annotations

import os
import re
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk

from PIL import Image, ImageOps, ImageTk


ROOT = Path(__file__).resolve().parents[1]
TOOLS_ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))

from backend.content import CHAMPIONS  # noqa: E402
from champion_portrait_io import (  # noqa: E402
    CHAMPION_ROOT, available_variants, read_manifest, record_variant, remove_variant,
    save_variant, variant_directory, write_manifest,
)


SUPPORTED_IMAGES = [("Image files", "*.png *.jpg *.jpeg *.webp"), ("All files", "*.*")]
COMMON_EXPRESSIONS = ("happy", "angry", "injured", "victory", "sad", "surprised", "focused")


def expression_slug(value: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")
    return value


class ChampionPortraitManager(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Fortcamp Champion Portrait Manager")
        self.geometry("1180x760")
        self.minsize(980, 650)
        self.catalog = sorted(CHAMPIONS.items(), key=lambda item: item[1]["name"].casefold())
        self.filtered = list(self.catalog)
        self.selected_id: str | None = None
        self.preview_photo: ImageTk.PhotoImage | None = None
        self.search_value = tk.StringVar()
        self.status_value = tk.StringVar(value="Select a Champion to begin.")
        self.heading_value = tk.StringVar(value="Champion Portraits")
        self.details_value = tk.StringVar(value="")
        self.source_value = tk.StringVar(value="")
        self._build_ui()
        self.search_value.trace_add("write", lambda *_: self.refresh_champion_list())
        self.refresh_champion_list()
        if self.filtered:
            self.champion_list.selection_set(0)
            self._select_champion()

    def _build_ui(self) -> None:
        style = ttk.Style(self)
        if "vista" in style.theme_names():
            style.theme_use("vista")
        style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"))
        style.configure("Heading.TLabel", font=("Segoe UI", 12, "bold"))
        style.configure("Status.TLabel", foreground="#385a3b")

        shell = ttk.Frame(self, padding=14)
        shell.pack(fill="both", expand=True)
        shell.columnconfigure(1, weight=1)
        shell.rowconfigure(1, weight=1)

        ttk.Label(shell, text="Fortcamp Champion Portrait Manager", style="Title.TLabel").grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 12)
        )

        left = ttk.Frame(shell, padding=(0, 0, 12, 0))
        left.grid(row=1, column=0, sticky="nsew")
        left.rowconfigure(2, weight=1)
        ttk.Label(left, text="Find Champion", style="Heading.TLabel").grid(row=0, column=0, sticky="w")
        search = ttk.Entry(left, textvariable=self.search_value, width=32)
        search.grid(row=1, column=0, sticky="ew", pady=(6, 8))
        self.champion_list = tk.Listbox(left, width=34, exportselection=False, activestyle="none")
        champion_scroll = ttk.Scrollbar(left, orient="vertical", command=self.champion_list.yview)
        self.champion_list.configure(yscrollcommand=champion_scroll.set)
        self.champion_list.grid(row=2, column=0, sticky="nsew")
        champion_scroll.grid(row=2, column=1, sticky="ns")
        self.champion_list.bind("<<ListboxSelect>>", lambda _event: self._select_champion())

        center = ttk.Frame(shell, padding=(12, 0))
        center.grid(row=1, column=1, sticky="nsew")
        center.columnconfigure(0, weight=1)
        center.rowconfigure(2, weight=1)
        ttk.Label(center, textvariable=self.heading_value, style="Title.TLabel").grid(row=0, column=0)
        ttk.Label(center, textvariable=self.details_value).grid(row=1, column=0, pady=(2, 10))
        self.preview = ttk.Label(center, text="No portrait", anchor="center", relief="solid", padding=4)
        self.preview.grid(row=2, column=0, sticky="nsew")
        ttk.Label(center, textvariable=self.source_value, wraplength=500, justify="center").grid(
            row=3, column=0, pady=(10, 0)
        )

        right = ttk.Frame(shell, padding=(12, 0, 0, 0))
        right.grid(row=1, column=2, sticky="nsew")
        right.rowconfigure(1, weight=1)
        ttk.Label(right, text="Portrait Variants", style="Heading.TLabel").grid(row=0, column=0, sticky="w")
        self.variant_list = tk.Listbox(right, width=27, height=14, exportselection=False, activestyle="none")
        self.variant_list.grid(row=1, column=0, sticky="nsew", pady=(6, 10))
        self.variant_list.bind("<<ListboxSelect>>", lambda _event: self.show_selected_variant())

        buttons = ttk.Frame(right)
        buttons.grid(row=2, column=0, sticky="ew")
        for index in range(1):
            buttons.columnconfigure(index, weight=1)
        ttk.Button(buttons, text="Set / Replace Default", command=self.replace_default).grid(row=0, column=0, sticky="ew", pady=3)
        ttk.Button(buttons, text="Add Expression Variant", command=self.add_expression).grid(row=1, column=0, sticky="ew", pady=3)
        ttk.Button(buttons, text="Replace Selected Variant", command=self.replace_selected).grid(row=2, column=0, sticky="ew", pady=3)
        ttk.Button(buttons, text="Delete Selected Variant", command=self.delete_selected).grid(row=3, column=0, sticky="ew", pady=3)
        ttk.Separator(buttons).grid(row=4, column=0, sticky="ew", pady=8)
        ttk.Button(buttons, text="Open Character Folder", command=self.open_character_folder).grid(row=5, column=0, sticky="ew", pady=3)
        ttk.Button(buttons, text="Open Source Sheet", command=self.open_source_sheet).grid(row=6, column=0, sticky="ew", pady=3)
        ttk.Button(buttons, text="Refresh", command=self.refresh_selected).grid(row=7, column=0, sticky="ew", pady=3)

        status = ttk.Label(shell, textvariable=self.status_value, style="Status.TLabel", anchor="w")
        status.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(12, 0))

    def refresh_champion_list(self) -> None:
        query = self.search_value.get().strip().casefold()
        current = self.selected_id
        self.filtered = [
            item for item in self.catalog
            if query in item[0].casefold() or query in item[1]["name"].casefold() or query in item[1]["series"].casefold()
        ]
        self.champion_list.delete(0, tk.END)
        selected_index = None
        for index, (champion_id, profile) in enumerate(self.filtered):
            self.champion_list.insert(tk.END, f"{profile['name']}  ·  {profile['series']}")
            if champion_id == current:
                selected_index = index
        if selected_index is not None:
            self.champion_list.selection_set(selected_index)
            self.champion_list.see(selected_index)

    def _select_champion(self) -> None:
        selection = self.champion_list.curselection()
        if not selection:
            return
        self.selected_id, profile = self.filtered[selection[0]]
        self.heading_value.set(profile["name"])
        self.details_value.set(f"{profile['series']}  ·  ID: {self.selected_id}")
        self.refresh_selected()

    def refresh_selected(self, preferred_variant: str | None = None) -> None:
        if not self.selected_id:
            return
        variants = available_variants(self.selected_id)
        self.variant_list.delete(0, tk.END)
        for variant in variants:
            self.variant_list.insert(tk.END, variant)
        desired = preferred_variant if preferred_variant in variants else "default" if "default" in variants else variants[0] if variants else None
        if desired:
            index = variants.index(desired)
            self.variant_list.selection_set(index)
            self.variant_list.see(index)
        manifest = read_manifest()
        source = manifest.get("champions", {}).get(self.selected_id, {}).get("source", {})
        if source:
            self.source_value.set(f"Source: {source.get('sheet', 'unknown')} · {source.get('cell', 'unknown')} · Batch {source.get('batch', '?')}")
        else:
            self.source_value.set("No contact-sheet source recorded.")
        self.show_selected_variant()

    def selected_variant(self) -> str | None:
        selection = self.variant_list.curselection()
        return self.variant_list.get(selection[0]) if selection else None

    def show_selected_variant(self) -> None:
        if not self.selected_id:
            return
        variant = self.selected_variant()
        if not variant:
            self.preview.configure(image="", text="No portrait imported")
            self.preview_photo = None
            return
        path = variant_directory(self.selected_id, variant) / "full.webp"
        try:
            with Image.open(path) as opened:
                preview = ImageOps.contain(opened.convert("RGB"), (500, 500), Image.Resampling.LANCZOS)
            self.preview_photo = ImageTk.PhotoImage(preview)
            self.preview.configure(image=self.preview_photo, text="")
            self.status_value.set(f"Viewing {self.selected_id}:{variant}")
        except (OSError, FileNotFoundError) as exc:
            self.preview.configure(image="", text=f"Could not load portrait\n{exc}")
            self.preview_photo = None

    def choose_image(self) -> Path | None:
        selected = filedialog.askopenfilename(title="Choose portrait image", filetypes=SUPPORTED_IMAGES)
        return Path(selected) if selected else None

    def import_variant(self, variant: str, image_path: Path) -> None:
        exists = (variant_directory(self.selected_id, variant) / "full.webp").is_file()
        if exists and not messagebox.askyesno(
            "Replace portrait?", f"Replace {self.heading_value.get()}'s '{variant}' portrait?"
        ):
            return
        try:
            with Image.open(image_path) as opened:
                save_variant(opened.copy(), self.selected_id, variant, replace=exists)
            manifest = read_manifest()
            record_variant(manifest, self.selected_id, variant)
            write_manifest(manifest)
            self.refresh_selected(variant)
            self.status_value.set(f"Imported {self.selected_id}:{variant} from {image_path.name}")
        except Exception as exc:
            messagebox.showerror("Import failed", str(exc))

    def replace_default(self) -> None:
        if not self.selected_id:
            return
        image_path = self.choose_image()
        if image_path:
            self.import_variant("default", image_path)

    def add_expression(self) -> None:
        if not self.selected_id:
            return
        suggestion = simpledialog.askstring(
            "Expression name",
            "Name this expression (examples: happy, angry, injured, victory):",
            initialvalue=COMMON_EXPRESSIONS[0], parent=self,
        )
        if suggestion is None:
            return
        variant = expression_slug(suggestion)
        if not variant or variant == "default":
            messagebox.showerror("Invalid expression", "Use a descriptive expression name other than 'default'.")
            return
        image_path = self.choose_image()
        if image_path:
            self.import_variant(variant, image_path)

    def replace_selected(self) -> None:
        variant = self.selected_variant()
        if not self.selected_id or not variant:
            messagebox.showinfo("No variant selected", "Select a portrait variant first.")
            return
        image_path = self.choose_image()
        if image_path:
            self.import_variant(variant, image_path)

    def delete_selected(self) -> None:
        variant = self.selected_variant()
        if not self.selected_id or not variant:
            messagebox.showinfo("No variant selected", "Select a portrait variant first.")
            return
        warning = "This removes the Champion's main portrait." if variant == "default" else "This removes only this expression."
        if not messagebox.askyesno("Delete portrait?", f"Delete {self.heading_value.get()}'s '{variant}' portrait?\n\n{warning}"):
            return
        try:
            remove_variant(self.selected_id, variant)
            self.refresh_selected()
            self.status_value.set(f"Deleted {self.selected_id}:{variant}")
        except Exception as exc:
            messagebox.showerror("Delete failed", str(exc))

    def open_character_folder(self) -> None:
        if not self.selected_id:
            return
        folder = CHAMPION_ROOT / self.selected_id
        folder.mkdir(parents=True, exist_ok=True)
        os.startfile(folder)  # type: ignore[attr-defined]

    def open_source_sheet(self) -> None:
        if not self.selected_id:
            return
        manifest = read_manifest()
        sheet = manifest.get("champions", {}).get(self.selected_id, {}).get("source", {}).get("sheet")
        path = ROOT / "champions" / sheet if sheet else None
        if not path or not path.is_file():
            messagebox.showinfo("Source unavailable", "No source contact sheet was found for this Champion.")
            return
        os.startfile(path)  # type: ignore[attr-defined]


def main() -> None:
    app = ChampionPortraitManager()
    app.mainloop()


if __name__ == "__main__":
    main()
