from __future__ import annotations

import logging
from typing import Optional

import speech_recognition as sr

from .speech import speak


logger = logging.getLogger("soika")


def listen_command() -> str:
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Soika слушает...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
        command = recognizer.recognize_google(audio, language="ru-RU")
        if not command or command.strip() == "":
            speak("Я не поняла вашу команду, Soika.")
            return ""
        print(f"Вы сказали: {command}")
        logger.info(f"Распознана команда: {command}")
        return command.lower()
    except (sr.WaitTimeoutError, sr.UnknownValueError):
        speak("Я не поняла вашу команду, Soika.")
    except sr.RequestError as exc:
        logger.error(f"Ошибка распознавания речи: {exc}")
        speak("Произошла ошибка при распознавании речи.")
    except Exception as exc:  # pragma: no cover
        logger.error(f"Неожиданная ошибка при распознавании: {exc}")
        speak("Произошла неожиданная ошибка.")
    return ""


