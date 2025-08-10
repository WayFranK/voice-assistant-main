from __future__ import annotations

import datetime
import threading
import time

from ..speech import speak
from ..utils import error_handler
from ..state import state


@error_handler
def set_timer(duration: str) -> None:
    try:
        if not duration or duration.strip() == "":
            speak("Пожалуйста, укажите время для таймера.")
            return
        minutes = int(duration)
        if minutes <= 0:
            speak("Время таймера должно быть больше нуля.")
            return
        timer_id = f"timer_{len(state.timers)}"
        state.timers[timer_id] = {
            'duration': minutes,
            'start_time': datetime.datetime.now(),
            'end_time': datetime.datetime.now() + datetime.timedelta(minutes=minutes),
        }
        def timer_thread() -> None:
            time.sleep(minutes * 60)
            speak(f"Таймер на {minutes} минут завершен!")
            state.timers.pop(timer_id, None)
        threading.Thread(target=timer_thread, daemon=True).start()
        speak(f"Таймер на {minutes} минут установлен.")
    except ValueError:
        speak("Пожалуйста, укажите время в минутах.")


@error_handler
def set_alarm(time_str: str) -> None:
    try:
        try:
            hour, minute = map(int, time_str.split(':'))
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError("Неверный формат времени")
        except ValueError:
            speak("Пожалуйста, укажите время в формате ЧЧ:ММ (например, 08:30)")
            return
        alarm_id = f"alarm_{len(state.alarms)}"
        state.alarms[alarm_id] = {
            'time': time_str,
            'hour': hour,
            'minute': minute,
            'created': datetime.datetime.now().isoformat(),
        }
        def alarm_checker() -> None:
            while True:
                now = datetime.datetime.now()
                if now.hour == hour and now.minute == minute:
                    speak(f"Будильник! Время {time_str}")
                    state.alarms.pop(alarm_id, None)
                    break
                time.sleep(30)
        threading.Thread(target=alarm_checker, daemon=True).start()
        speak(f"Будильник на {time_str} установлен.")
    except Exception:
        speak("Не удалось установить будильник.")


