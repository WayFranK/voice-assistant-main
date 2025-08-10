from __future__ import annotations

import webbrowser
from urllib.parse import quote

from ..speech import speak
from ..utils import error_handler


@error_handler
def open_website(site_name: str) -> None:
    if not site_name or site_name.strip() == "":
        speak("Пожалуйста, укажите название сайта.")
        return
    sites = {
        'google': 'https://www.google.com',
        'яндекс': 'https://www.yandex.ru',
        'youtube': 'https://www.youtube.com',
        'gmail': 'https://mail.google.com',
        'почта': 'https://mail.yandex.ru'
    }
    url = sites.get(site_name, f'https://{site_name}' if not site_name.startswith('http') else site_name)
    webbrowser.open(url)
    speak(f"Открываю {site_name}.")


@error_handler
def search_web(query: str) -> None:
    if not query or query.strip() == "":
        speak("Пожалуйста, укажите что искать.")
        return
    webbrowser.open(f"https://www.google.com/search?q={quote(query)}")
    speak(f"Ищу {query} в интернете.")


@error_handler
def translate_text(text: str) -> None:
    if not text or text.strip() == "":
        speak("Пожалуйста, укажите текст для перевода.")
        return
    webbrowser.open(f"https://translate.google.com/?sl=ru&tl=en&text={quote(text)}")
    speak(f"Перевожу '{text}' на английский.")


@error_handler
def search_images(query: str) -> None:
    if not query or query.strip() == "":
        speak("Пожалуйста, укажите что искать.")
        return
    webbrowser.open(f"https://www.google.com/search?q={quote(query)}&tbm=isch")
    speak(f"Ищу изображения по запросу {query}.")


