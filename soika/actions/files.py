from __future__ import annotations

import os
import subprocess
from pathlib import Path

from ..speech import speak
from ..utils import error_handler


@error_handler
def create_folder(folder_name: str) -> None:
    if not folder_name or folder_name.strip() == "":
        speak("Пожалуйста, укажите название папки.")
        return
    folder_path = Path(folder_name)
    folder_path.mkdir(exist_ok=True)
    speak(f"Папка {folder_name} создана.")


@error_handler
def search_file(filename: str) -> None:
    if not filename or filename.strip() == "":
        speak("Пожалуйста, укажите название файла для поиска.")
        return
    result = subprocess.run(['where', filename], capture_output=True, text=True)
    if result.returncode == 0:
        speak(f"Файл {filename} найден.")
        print(f"Путь: {result.stdout}")
    else:
        speak(f"Файл {filename} не найден.")


@error_handler
def open_folder(folder_name: str) -> None:
    if not folder_name or folder_name.strip() == "":
        speak("Пожалуйста, укажите название папки.")
        return
    folder_path = Path(folder_name)
    if not folder_path.exists():
        speak(f"Папка {folder_name} не существует.")
        return
    os.system(f'explorer "{folder_name}"')
    speak(f"Открываю папку {folder_name}.")


