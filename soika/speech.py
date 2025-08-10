from __future__ import annotations

import logging
import pyttsx3


logger = logging.getLogger("soika")


class Speaker:
    def __init__(self, rate: int = 150, volume: float = 0.9) -> None:
        self._engine = pyttsx3.init()
        self._engine.setProperty('rate', rate)
        self._engine.setProperty('volume', volume)

    def say(self, text: str) -> None:
        if not text or text.strip() == "":
            return
        try:
            self._engine.say(text)
            self._engine.runAndWait()
            logger.info(f"Soika сказала: {text}")
        except Exception as exc:  # pragma: no cover
            logger.error(f"Ошибка при озвучивании: {exc}")
            print(f"Soika: {text}")


speaker = Speaker()


def speak(text: str) -> None:
    speaker.say(text)


