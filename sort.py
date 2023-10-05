import sys
import re
import shutil
from pathlib import Path


CATEGORIES = {
    "Audio": [".mp3", ".ogg", ".wav", ".amr"],
    "Image": [".jpeg", ".png", ".jpg", ".mkv"],
    "Docs": [".doc", ".docx", ".txt", ".pdf", ".xlsx", ".pptx"],
    "Archives": [".zip", ".gz", ".tar"],
    "Video": [".avi", ".mp4", ".mov", ".mkv"]
    }


def unpack_archives(path:Path, archive_folder: str = "Archives") -> None:
    archive_path = path / archive_folder
    if not archive_path.is_dir():
        return
    
    formats = set(fmt[0] for fmt in shutil.get_unpack_formats())
    
    for archive_file in archive_path.glob("**/*"):
        if archive_file.is_file() and archive_file.suffix[1:] in formats:
            try:
                #.stem для видалення останнього елемента (.zip) 
                unpack_path = archive_path / archive_file.stem
                # (exist_ok=T) для того щоб неповерав помилки якщо дирек. існує
                unpack_path.mkdir(exist_ok=True)
                shutil.unpack_archive(str(archive_file), str(unpack_path))
                archive_file.unlink() # видаляє архів 
            except Exception:
                return


def remove_empty_foders(path:Path) -> None:
    for folder in sorted(path.glob("**/"), key=lambda x: len(x.parts), 
    reverse=True):
        if folder.is_dir() and not any(folder.iterdir()) :
            try:
                folder.rmdir()
            except Exception:
                return None
        

def move_file(file_name:str, category:str, root_dir:Path, element:Path) -> None:
    target_dir = root_dir.joinpath(category)
    if not target_dir.exists():
        target_dir.mkdir()
    element.replace(target_dir.joinpath(file_name))


def get_categories(file:Path) -> str:
    ext = file.suffix.lower()
    for cat, exts in CATEGORIES.items():
        if ext in exts:
            return cat
    return "Other"


def normalize(file_name) -> str:
    new_name_file = []
    for char in file_name:
        if re.match(r"[\u0410-\u044F]", char):
            new_name_file.append("_")
        else:
            new_name_file.append(char)
    return "".join(new_name_file)


def sort_folder(path:Path) -> None:
    for element in path.glob("**/*"):
        if element.is_file():
            normalize_name = normalize(element.name)
            category = get_categories(element)
            move_file(normalize_name, category, path, element)

    remove_empty_foders(path)
    unpack_archives(path)        

def main() -> str:
    try:
        path = Path(sys.argv[1])
    except IndexError:
        return "Not path to folder"
    
    if not path.exists():
        return "Folder dos not exists"
    
    sort_folder(path)


if __name__ == "__main__":
    main()
