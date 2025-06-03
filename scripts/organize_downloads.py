#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["rich"]
# ///

import shutil
from pathlib import Path
from rich import print

# Define the downloads directory
DOWNLOADS_DIR = Path.home() / "Downloads"

# Mapping of file types / keywords to folder names
CATEGORY_MAP = {
    "pdf": "PDFs",
    "pptx": "Presentations",
    "mp4": "Videos",
    "m4a": "Audio",
    "png": "Images",
    "jpg": "Images",
    "jpeg": "Images",
    "webp": "Images",
    "heic": "Images",
    "dmg": "Installers",
    "zip": "Archives",
    "rar": "Archives",
    "csv": "Data",
    "xlsx": "Data",
    "json": "Data",
    "srt": "Subtitles",
    "ics": "Calendars",
    "ipynb": "Notebooks",
    "tsx": "Code",
    "html": "Web",
    "txt": "Text",
}

KEYWORD_FOLDERS = {
    "invoice": "Invoices",
    "receipt": "Invoices",
    "fatura": "Invoices",
    "anki": "Anki",
    "course": "Courses",
    "blueprint": "Courses",
    "ai": "AI",
    "langgraph": "AI",
    "agent": "AI",
    "prompt": "AI",
    "filmmaking": "Media Projects",
    "presentation": "Presentations",
}


def get_target_folder(file: Path) -> Path:
    # Check by keyword first
    lower_name = file.name.lower()
    for keyword, folder in KEYWORD_FOLDERS.items():
        if keyword in lower_name:
            return DOWNLOADS_DIR / folder

    # Check by extension
    ext = file.suffix.lower().strip(".")
    if ext in CATEGORY_MAP:
        return DOWNLOADS_DIR / CATEGORY_MAP[ext]

    return DOWNLOADS_DIR / "Misc"


def organize_downloads():
    print(f"[bold yellow]Organizing files in {DOWNLOADS_DIR}...[/bold yellow]")
    for file in DOWNLOADS_DIR.iterdir():
        if file.is_file():
            target_folder = get_target_folder(file)
            target_folder.mkdir(exist_ok=True)

            target_path = target_folder / file.name
            if target_path.exists():
                print(f"[red]File already exists:[/red] {target_path}")
                continue

            try:
                shutil.move(str(file), target_path)
                print(f"[green]Moved:[/green] {file.name} -> {target_folder.name}")
            except Exception as e:
                print(f"[red]Error moving {file.name}:[/red] {e}")


if __name__ == "__main__":
    organize_downloads()
