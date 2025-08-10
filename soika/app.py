from __future__ import annotations

import logging
import threading
import time

from .logging_config import configure_logging
from .speech import speak
from .voice import listen_command
from .background import background_clear_memory, background_check_memory
from .commands import (
    shutdown_computer, restart_computer, lock_computer, clear_memory, open_task_manager, open_explorer,
    open_website, search_web, translate_text, search_images,
    search_file, open_folder, create_folder,
    control_music,
    get_date, get_time, get_weather,
    add_note, read_notes, add_reminder,
    set_timer, set_alarm,
    toggle_privacy_mode, toggle_learning_mode, toggle_do_not_disturb,
    show_activity_logs, clear_yesterday_data, get_system_insights, adapt_to_game,
)
from .monitoring.screen import toggle_monitoring


logger = configure_logging()


def process_command(command: str) -> None:
    if not command or command.strip() == "":
        speak("Я не получила команду для обработки.")
        return

    # Системные команды
    if any(phrase in command for phrase in ['заверши работу компьютера', 'выключи компьютер', 'выключи пк']):
        shutdown_computer()
    elif any(phrase in command for phrase in ['перезагрузи компьютер', 'перезапусти компьютер']):
        restart_computer()
    elif any(phrase in command for phrase in ['заблокируй компьютер', 'заблокируй экран']):
        lock_computer()
    elif any(phrase in command for phrase in ['очисти память', 'очисти кэш', 'освободи ресурсы']):
        clear_memory()
    elif 'открой диспетчер задач' in command:
        open_task_manager()
    elif 'открой проводник' in command:
        open_explorer()
    elif 'создай папку' in command:
        folder_name = command.replace('создай папку', '').strip()
        create_folder(folder_name) if folder_name else speak("Пожалуйста, укажите название папки.")
    # Интернет и браузер
    elif 'открой google' in command:
        open_website('google')
    elif 'открой яндекс' in command:
        open_website('яндекс')
    elif 'открой youtube' in command:
        open_website('youtube')
    elif 'открой почту' in command:
        open_website('почта')
    elif command.startswith('открой ') and 'открой google' not in command and 'открой яндекс' not in command:
        open_website(command.replace('открой ', '').strip())
    elif command.startswith('найди ') and all(x not in command for x in ['картинку', 'файл', 'документ', 'музыку']):
        search_web(command.replace('найди ', '').strip())
    elif command.startswith('переведи '):
        translate_text(command.replace('переведи ', '').replace(' на английский', '').strip())
    elif command.startswith('найди картинку '):
        search_images(command.replace('найди картинку ', '').strip())
    # Поиск на компьютере
    elif command.startswith('найди файл '):
        search_file(command.replace('найди файл ', '').strip())
    elif command.startswith('открой папку '):
        open_folder(command.replace('открой папку ', '').strip())
    elif command.startswith('найди документ '):
        search_file(command.replace('найди документ ', '').strip())
    elif command.startswith('найди музыку '):
        search_file(command.replace('найди музыку ', '').strip())
    # Мультимедиа
    elif 'включи музыку' in command:
        control_music('play')
    elif 'поставь музыку на паузу' in command:
        control_music('pause')
    elif 'включи следующее' in command:
        control_music('next')
    elif 'сделай громче' in command:
        control_music('volume_up')
    elif 'сделай тише' in command:
        control_music('volume_down')
    elif command.startswith('открой фильм '):
        search_web(f"смотреть {command.replace('открой фильм ', '').strip()} онлайн")
    # Разное
    elif 'какой сегодня день' in command:
        get_date()
    elif 'который час' in command or 'сколько времени' in command:
        get_time()
    elif 'какая погода' in command:
        get_weather()
    elif command.startswith('напомни мне ') and ' в ' in command:
        parts = command.replace('напомни мне ', '').split(' в ')
        if len(parts) == 2:
            add_reminder(parts[0].strip(), parts[1].strip())
        else:
            speak("Пожалуйста, укажите время напоминания.")
    elif command.startswith('запиши заметку '):
        add_note(command.replace('запиши заметку ', '').strip())
    elif 'прочитай заметки' in command:
        read_notes()
    elif command.startswith('включи таймер на '):
        set_timer(command.replace('включи таймер на ', '').replace(' минут', '').strip())
    elif command.startswith('включи будильник на '):
        set_alarm(command.replace('включи будильник на ', '').strip())
    # Система мониторинга и обучения
    elif 'включи мониторинг экрана' in command or 'выключи мониторинг экрана' in command:
        toggle_monitoring()
    elif 'включи режим конфиденциальности' in command:
        toggle_privacy_mode()
    elif 'начни обучение поведения' in command or 'останови обучение' in command:
        toggle_learning_mode()
    elif command.startswith('адаптируйся к игре '):
        adapt_to_game(command.replace('адаптируйся к игре ', '').strip().strip('"'))
    elif 'включи режим не беспокоить' in command:
        toggle_do_not_disturb()
    elif 'покажи логи активности' in command:
        show_activity_logs()
    elif 'забудь данные за вчера' in command:
        clear_yesterday_data()
    elif 'какие у тебя догадки' in command:
        get_system_insights()
    # Базовые команды
    elif 'привет' in command:
        speak("Привет! Я Soika, как я могу помочь?")
    elif 'что ты можешь' in command or 'что ты умеешь' in command:
        speak("Я Soika, и я могу выполнять различные команды: управлять компьютером, работать с интернетом, искать файлы, управлять музыкой, устанавливать напоминания и таймеры, а также многое другое.")
    elif any(x in command for x in ['расскажи шутку', 'пошути', 'шутка']):
        from .actions.misc import tell_joke
        tell_joke()
    else:
        speak("Я не знаю, как выполнить эту команду. Попробуйте сказать 'что ты можешь' для списка команд.")


def run_app() -> None:
    logger.info("Soika запущена")
    speak("Привет! Я Soika, ваш голосовой помощник. Как я могу помочь?")
    threading.Thread(target=background_clear_memory, args=(clear_memory,), daemon=True).start()
    threading.Thread(target=background_check_memory, daemon=True).start()
    while True:
        try:
            command = listen_command()
            if command:
                process_command(command)
        except KeyboardInterrupt:
            logger.info("Soika остановлена пользователем")
            speak("До свидания!")
            break
        except Exception:
            logger.error("Критическая ошибка", exc_info=True)
            speak("Произошла критическая ошибка. Перезапускаюсь...")
            time.sleep(2)
        except SystemExit:
            logger.info("Soika завершена системой")
            speak("До свидания!")
            break


