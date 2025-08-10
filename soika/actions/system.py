from __future__ import annotations

import os
import time
import psutil

from ..speech import speak
from ..utils import error_handler


@error_handler
def shutdown_computer() -> None:
    speak("Выключаю компьютер через 10 секунд.")
    time.sleep(10)
    os.system("shutdown /s /t 0")


@error_handler
def restart_computer() -> None:
    speak("Перезагружаю компьютер через 10 секунд.")
    time.sleep(10)
    os.system("shutdown /r /t 0")


@error_handler
def lock_computer() -> None:
    os.system("rundll32.exe user32.dll,LockWorkStation")
    speak("Компьютер заблокирован.")


@error_handler
def clear_memory() -> None:
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] in ['chrome.exe', 'firefox.exe', 'msedge.exe']:
                try:
                    proc.kill()
                except Exception:
                    pass
        os.system("ipconfig /flushdns")
        speak("Память очищена, фоновые процессы закрыты.")
    except Exception:
        speak("Частично очистила память.")


@error_handler
def open_task_manager() -> None:
    os.system("taskmgr")
    speak("Открываю диспетчер задач.")


@error_handler
def open_explorer() -> None:
    os.system("explorer")
    speak("Открываю проводник.")


