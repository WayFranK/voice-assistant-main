from __future__ import annotations

import time
import psutil

from .speech import speak


def background_clear_memory(clear_fn) -> None:
    while True:
        try:
            time.sleep(60)
            clear_fn()
        except Exception:
            pass
        except KeyboardInterrupt:
            break


def background_check_memory() -> None:
    warned = False
    while True:
        try:
            time.sleep(30)
            mem = psutil.virtual_memory()
            if mem.percent >= 80 and not warned:
                speak(f"Внимание! Использование оперативной памяти {mem.percent} процентов.")
                warned = True
            elif mem.percent < 80:
                warned = False
        except Exception:
            pass
        except KeyboardInterrupt:
            break


