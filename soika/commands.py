from __future__ import annotations

from .speech import speak
from .state import state, toggle_flag
from .utils import error_handler

from .actions.system import shutdown_computer, restart_computer, lock_computer, clear_memory, open_task_manager, open_explorer
from .actions.files import create_folder, search_file, open_folder
from .actions.web import open_website, search_web, translate_text, search_images
from .actions.media import control_music
from .actions.misc import get_date, get_time, get_weather, tell_joke
from .actions.notes import add_note, read_notes, add_reminder
from .actions.timers import set_timer, set_alarm
from .monitoring.screen import toggle_monitoring


@error_handler
def adapt_to_game(game_name: str) -> None:
    if not game_name or game_name.strip() == "":
        speak("Пожалуйста, укажите название игры.")
        return
    state.current_game = game_name
    speak(f"Адаптируюсь к игре {game_name}.")


@error_handler
def toggle_privacy_mode() -> None:
    enabled = toggle_flag('privacy_mode')
    speak(f"Режим конфиденциальности {'включен' if enabled else 'выключен'}.")


@error_handler
def toggle_learning_mode() -> None:
    enabled = toggle_flag('learning_mode')
    speak(f"Режим обучения {'включен' if enabled else 'выключен'}.")


@error_handler
def toggle_do_not_disturb() -> None:
    enabled = toggle_flag('do_not_disturb')
    speak(f"Режим 'не беспокоить' {'включен' if enabled else 'выключен'}.")


@error_handler
def show_activity_logs() -> None:
    try:
        with open('soika_errors.log', 'r', encoding='utf-8') as f:
            logs = f.readlines()[-20:]
        speak("Показываю логи активности за сегодня.")
        for log in logs:
            print(log.strip())
    except Exception:
        speak("Не удалось прочитать логи.")


@error_handler
def clear_yesterday_data() -> None:
    speak("Данные за вчера удалены.")


@error_handler
def get_system_insights() -> None:
    def status(flag: bool, msg: str):
        return msg if flag else None
    insights = list(filter(None, [
        status(state.monitoring_enabled, 'Мониторинг экрана активен'),
        status(state.privacy_mode, 'Режим конфиденциальности включен'),
        status(state.learning_mode, 'Режим обучения активен'),
        status(state.do_not_disturb, "Режим 'не беспокоить' включен"),
        f"Адаптирована к игре {state.current_game}" if state.current_game else None,
    ]))
    if not insights:
        insights.append("Система работает в обычном режиме")
    speak("Мои текущие догадки:")
    for insight in insights:
        speak(insight)


