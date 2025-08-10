from __future__ import annotations

import datetime
import logging
import os
from pathlib import Path
from typing import Optional

import tkinter as tk
from PIL import Image, ImageTk
import pyautogui

from ..speech import speak
from ..state import state
from ..utils import error_handler


logger = logging.getLogger("soika")

MONITOR_DIR = Path('screen_monitor')
MONITOR_DIR.mkdir(exist_ok=True)
MAX_SCREENSHOTS = 100
MONITOR_INTERVAL = 2  # seconds


def _clear_old_screenshots() -> None:
    try:
        files = sorted(MONITOR_DIR.glob('*.png'), key=os.path.getmtime)
        while len(files) > MAX_SCREENSHOTS:
            try:
                os.remove(files[0])
                files.pop(0)
            except Exception as exc:
                logger.error(f"Ошибка удаления скриншота: {exc}")
                break
    except Exception as exc:
        logger.error(f"Ошибка при очистке старых скриншотов: {exc}")


def _take_screenshot() -> Optional[Path]:
    try:
        img = pyautogui.screenshot()
        ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        path = MONITOR_DIR / f'screen_{ts}.png'
        img.save(path)
        _clear_old_screenshots()
        return path
    except Exception as exc:
        logger.error(f"Ошибка при создании скриншота: {exc}")
        return None


class ScreenMonitorWindow:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title('Мониторинг экрана Soika')
        self.label = tk.Label(root)
        self.label.pack()
        self.update_image()

    def update_image(self) -> None:
        try:
            path = _take_screenshot()
            if path is None:
                self.root.after(MONITOR_INTERVAL * 1000, self.update_image)
                return
            img = Image.open(path)
            img = img.resize((800, 450))
            self.photo = ImageTk.PhotoImage(img)
            self.label.config(image=self.photo)
            self.root.after(MONITOR_INTERVAL * 1000, self.update_image)
        except Exception as exc:
            logger.error(f"Ошибка при обновлении изображения: {exc}")
            self.root.after(MONITOR_INTERVAL * 1000, self.update_image)


_monitor_window_thread = None


@error_handler
def toggle_monitoring() -> None:
    if not state.monitoring_enabled:
        state.monitoring_enabled = True
        speak('Мониторинг экрана включен.')
        _start_screen_monitor()
    else:
        _stop_screen_monitor()


def _start_screen_monitor() -> None:
    import threading

    def run_window() -> None:
        try:
            root = tk.Tk()
            state.monitor_window = root
            _ = ScreenMonitorWindow(root)
            root.protocol("WM_DELETE_WINDOW", lambda: _stop_screen_monitor())
            root.mainloop()
        except Exception as exc:
            logger.error(f"Ошибка при запуске мониторинга экрана: {exc}")
            state.monitoring_enabled = False

    global _monitor_window_thread
    if _monitor_window_thread and _monitor_window_thread.is_alive():
        return
    _monitor_window_thread = threading.Thread(target=run_window, daemon=True)
    _monitor_window_thread.start()


def _stop_screen_monitor() -> None:
    state.monitoring_enabled = False
    win = state.monitor_window
    if win:
        try:
            win.quit()
            win.destroy()
        except Exception as exc:
            logger.error(f"Ошибка при закрытии окна мониторинга: {exc}")
        finally:
            state.monitor_window = None
    speak('Мониторинг экрана выключен.')


