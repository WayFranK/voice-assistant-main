from __future__ import annotations

import datetime
import random

from ..speech import speak
from ..utils import error_handler


@error_handler
def get_date() -> None:
    now = datetime.datetime.now()
    speak(f"Сегодня {now.strftime('%d %B %Y, %A')}")


@error_handler
def get_time() -> None:
    speak(f"Сейчас {datetime.datetime.now().strftime('%H:%M')}")


@error_handler
def get_weather() -> None:
    speak("К сожалению, функция погоды пока не реализована.")


@error_handler
def tell_joke() -> None:
    jokes = [
        "Почему программисты не ходят в лес? Потому что там много багов.",
        "Какой язык программирования предпочитают океаны? Си.",
        "Почему питоны никогда не устают? Потому что они всегда остаются гибкими.",
        "Почему Java-программисты всегда носят очки? Потому что они не могут C#.",
        "Что говорят разработчики, когда их код работает? Это магия!",
    ]
    speak(random.choice(jokes))


