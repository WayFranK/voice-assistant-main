from __future__ import annotations

import datetime
from typing import List, Dict, Any

from ..speech import speak
from ..utils import error_handler
from ..state import state


@error_handler
def add_reminder(text: str, time_str: str) -> None:
    if not text or text.strip() == "":
        speak("Пожалуйста, укажите текст напоминания.")
        return
    if not time_str or time_str.strip() == "":
        speak("Пожалуйста, укажите время напоминания.")
        return
    state.reminders.append({'text': text, 'time': time_str, 'created': datetime.datetime.now().isoformat()})
    speak(f"Напоминание '{text}' на {time_str} добавлено.")


@error_handler
def add_note(text: str) -> None:
    if not text or text.strip() == "":
        speak("Пожалуйста, укажите текст заметки.")
        return
    state.notes.append({'text': text, 'timestamp': datetime.datetime.now().isoformat()})
    speak(f"Заметка '{text}' добавлена.")


@error_handler
def read_notes() -> None:
    if not state.notes:
        speak("У вас нет заметок.")
        return
    speak("Ваши заметки:")
    for i, note in enumerate(state.notes, 1):
        speak(f"{i}. {note['text']}")


