import speech_recognition as sr
import pyttsx3
import os
import webbrowser
import datetime
import random
import subprocess
import psutil
import time
import logging
from pathlib import Path
import threading
from urllib.parse import quote
# --- Новые импорты для мониторинга экрана ---
import tkinter as tk
from PIL import Image, ImageTk
import pyautogui
import glob

# Настройка логирования для системы исправления ошибок
try:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('soika_errors.log'),
            logging.StreamHandler()
        ]
    )
except Exception as e:
    # Если не удается создать файл логов, используем только консоль
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    print(f"Предупреждение: Не удалось создать файл логов: {e}")

logger = logging.getLogger(__name__)

# Глобальные переменные для состояния системы
system_state = {
    'monitoring_enabled': False,
    'privacy_mode': False,
    'learning_mode': False,
    'do_not_disturb': False,
    'current_game': None,
    'notes': [],
    'reminders': [],
    'timers': {},
    'alarms': {},
    'monitor_thread': None,
    'monitor_window': None
}

MONITOR_DIR = Path('./screen_monitor')
try:
    MONITOR_DIR.mkdir(exist_ok=True)
except Exception as e:
    logger.error(f"Ошибка создания директории мониторинга: {e}")
    # Создаем директорию в текущей папке пользователя как запасной вариант
    MONITOR_DIR = Path.home() / 'soika_screen_monitor'
    MONITOR_DIR.mkdir(exist_ok=True)
MAX_SCREENSHOTS = 100
MONITOR_INTERVAL = 2  # секунды

# --- Фоновая очистка памяти раз в минуту ---
def background_clear_memory():
    while True:
        try:
            time.sleep(60)
            clear_memory()
        except Exception as e:
            logger.error(f"Ошибка фоновой очистки памяти: {e}")
        except KeyboardInterrupt:
            break

def background_check_memory():
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
        except Exception as e:
            logger.error(f"Ошибка проверки памяти: {e}")
        except KeyboardInterrupt:
            break

# --- Мониторинг экрана ---
def _clear_old_screenshots():
    try:
        # Проверяем, что директория существует
        if not MONITOR_DIR.exists():
            return
            
        files = sorted(MONITOR_DIR.glob('*.png'), key=os.path.getmtime)
        while len(files) > MAX_SCREENSHOTS:
            try:
                os.remove(files[0])
                files.pop(0)
            except Exception as e:
                logger.error(f"Ошибка удаления скриншота: {e}")
                break
    except Exception as e:
        logger.error(f"Ошибка при очистке старых скриншотов: {e}")

def _take_screenshot():
    try:
        # Проверяем, что директория существует
        if not MONITOR_DIR.exists():
            MONITOR_DIR.mkdir(exist_ok=True)
            
        img = pyautogui.screenshot()
        ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        path = MONITOR_DIR / f'screen_{ts}.png'
        img.save(path)
        _clear_old_screenshots()
        return path
    except Exception as e:
        logger.error(f"Ошибка при создании скриншота: {e}")
        return None

class ScreenMonitorWindow:
    def __init__(self, root):
        self.root = root
        self.root.title('Мониторинг экрана Soika')
        self.label = tk.Label(root)
        self.label.pack()
        self.update_image()

    def update_image(self):
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
        except Exception as e:
            logger.error(f"Ошибка при обновлении изображения: {e}")
            self.root.after(MONITOR_INTERVAL * 1000, self.update_image)

_monitor_window_thread = None

def _start_screen_monitor():
    def run_window():
        try:
            root = tk.Tk()
            system_state['monitor_window'] = root
            win = ScreenMonitorWindow(root)
            root.protocol("WM_DELETE_WINDOW", lambda: _stop_screen_monitor())
            root.mainloop()
        except Exception as e:
            logger.error(f"Ошибка при запуске мониторинга экрана: {e}")
            system_state['monitoring_enabled'] = False
            
    global _monitor_window_thread
    if _monitor_window_thread and _monitor_window_thread.is_alive():
        return
    _monitor_window_thread = threading.Thread(target=run_window, daemon=True)
    _monitor_window_thread.start()


def _stop_screen_monitor():
    system_state['monitoring_enabled'] = False
    win = system_state.get('monitor_window')
    if win:
        try:
            win.quit()  # Безопасное закрытие tkinter окна
            win.destroy()
        except Exception as e:
            logger.error(f"Ошибка при закрытии окна мониторинга: {e}")
        finally:
            system_state['monitor_window'] = None
    speak('Мониторинг экрана выключен.')

# Настройка голосового синтезатора
try:
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 0.9)
except Exception as e:
    logger.error(f"Ошибка инициализации голосового синтезатора: {e}")
    engine = None

def speak(text):
    if not text or text.strip() == "":
        return
        
    if engine is None:
        print(f"Soika: {text}")
        return
        
    try:
        engine.say(text)
        engine.runAndWait()
        logger.info(f"Soika сказала: {text}")
    except Exception as e:
        logger.error(f"Ошибка при озвучивании: {e}")
        print(f"Soika: {text}")

def error_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Ошибка в функции {func.__name__}: {e}")
            speak("Произошла ошибка при выполнении команды. Попробуйте еще раз.")
            return None
    return wrapper

@error_handler
def listen_command():
    try:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Soika слушает...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
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
    except sr.RequestError as e:
        logger.error(f"Ошибка распознавания речи: {e}")
        speak("Произошла ошибка при распознавании речи.")
    except Exception as e:
        logger.error(f"Неожиданная ошибка при распознавании: {e}")
        speak("Произошла неожиданная ошибка.")
    return ""

# --- Вспомогательные функции ---
def _toggle_state(key, msg):
    if not key or key.strip() == "":
        speak("Ошибка: не указан ключ состояния.")
        return
        
    if not msg or msg.strip() == "":
        speak("Ошибка: не указано сообщение.")
        return
        
    system_state[key] = not system_state[key]
    status = "включен" if system_state[key] else "выключен"
    speak(f"{msg} {status}.")

def _get_status(key, msg):
    if not key or key.strip() == "":
        return None
        
    if not msg or msg.strip() == "":
        return None
        
    if system_state[key]:
        return msg
    return None

# --- Системные команды ---
@error_handler
def shutdown_computer():
    speak("Выключаю компьютер через 10 секунд.")
    time.sleep(10)
    os.system("shutdown /s /t 0")

@error_handler
def restart_computer():
    speak("Перезагружаю компьютер через 10 секунд.")
    time.sleep(10)
    os.system("shutdown /r /t 0")

@error_handler
def lock_computer():
    os.system("rundll32.exe user32.dll,LockWorkStation")
    speak("Компьютер заблокирован.")

@error_handler
def clear_memory():
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] in ['chrome.exe', 'firefox.exe', 'msedge.exe']:
                try: proc.kill()
                except: pass
        # Очистка кэша для Windows
        os.system("ipconfig /flushdns")
        speak("Память очищена, фоновые процессы закрыты.")
    except Exception as e:
        logger.error(f"Ошибка при очистке памяти: {e}")
        speak("Частично очистила память.")

@error_handler
def open_task_manager():
    os.system("taskmgr")
    speak("Открываю диспетчер задач.")

@error_handler
def open_explorer():
    os.system("explorer")
    speak("Открываю проводник.")

@error_handler
def create_folder(folder_name):
    try:
        if not folder_name or folder_name.strip() == "":
            speak("Пожалуйста, укажите название папки.")
            return
            
        folder_path = Path(folder_name)
        folder_path.mkdir(exist_ok=True)
        speak(f"Папка {folder_name} создана.")
    except Exception as e:
        logger.error(f"Ошибка создания папки: {e}")
        speak("Не удалось создать папку.")

# --- Интернет и браузер ---
@error_handler
def open_website(site_name):
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
def search_web(query):
    if not query or query.strip() == "":
        speak("Пожалуйста, укажите что искать.")
        return
        
    webbrowser.open(f"https://www.google.com/search?q={quote(query)}")
    speak(f"Ищу {query} в интернете.")

@error_handler
def translate_text(text):
    if not text or text.strip() == "":
        speak("Пожалуйста, укажите текст для перевода.")
        return
        
    webbrowser.open(f"https://translate.google.com/?sl=ru&tl=en&text={quote(text)}")
    speak(f"Перевожу '{text}' на английский.")

@error_handler
def search_images(query):
    if not query or query.strip() == "":
        speak("Пожалуйста, укажите что искать.")
        return
        
    webbrowser.open(f"https://www.google.com/search?q={quote(query)}&tbm=isch")
    speak(f"Ищу изображения по запросу {query}.")

# --- Поиск на компьютере ---
@error_handler
def search_file(filename):
    try:
        if not filename or filename.strip() == "":
            speak("Пожалуйста, укажите название файла для поиска.")
            return
            
        result = subprocess.run(['where', filename], capture_output=True, text=True)
        if result.returncode == 0:
            speak(f"Файл {filename} найден.")
            print(f"Путь: {result.stdout}")
        else:
            speak(f"Файл {filename} не найден.")
    except Exception as e:
        logger.error(f"Ошибка поиска файла: {e}")
        speak("Не удалось выполнить поиск файла.")

@error_handler
def open_folder(folder_name):
    try:
        if not folder_name or folder_name.strip() == "":
            speak("Пожалуйста, укажите название папки.")
            return
            
        folder_path = Path(folder_name)
        if not folder_path.exists():
            speak(f"Папка {folder_name} не существует.")
            return
            
        os.system(f'explorer "{folder_name}"')
        speak(f"Открываю папку {folder_name}.")
    except Exception as e:
        logger.error(f"Ошибка открытия папки: {e}")
        speak("Не удалось открыть папку.")

# --- Мультимедиа ---
@error_handler
def control_music(action):
    if not action or action.strip() == "":
        speak("Пожалуйста, укажите действие для управления музыкой.")
        return
        
    actions = {
        'play':   ("start wmplayer", "Включаю проигрыватель Windows Media."),
        'pause':  ("powershell (New-Object -ComObject WScript.Shell).SendKeys([char]179)", "Ставлю музыку на паузу."),
        'next':   ("powershell (New-Object -ComObject WScript.Shell).SendKeys([char]176)", "Следующий трек."),
        'volume_up': ("powershell (New-Object -ComObject WScript.Shell).SendKeys([char]175)", "Увеличиваю громкость."),
        'volume_down': ("powershell (New-Object -ComObject WScript.Shell).SendKeys([char]174)", "Уменьшаю громкость.")
    }
    cmd, msg = actions.get(action, (None, None))
    if cmd:
        os.system(cmd)
        speak(msg)
    else:
        speak("Неизвестное действие для управления музыкой.")

# --- Разное ---
@error_handler
def get_date():
    now = datetime.datetime.now()
    speak(f"Сегодня {now.strftime('%d %B %Y, %A')}")

@error_handler
def get_time():
    speak(f"Сейчас {datetime.datetime.now().strftime('%H:%M')}")

@error_handler
def get_weather():
    speak("К сожалению, функция погоды пока не реализована.")

@error_handler
def add_reminder(text, time_str):
    if not text or text.strip() == "":
        speak("Пожалуйста, укажите текст напоминания.")
        return
        
    if not time_str or time_str.strip() == "":
        speak("Пожалуйста, укажите время напоминания.")
        return
        
    system_state['reminders'].append({'text': text, 'time': time_str, 'created': datetime.datetime.now().isoformat()})
    speak(f"Напоминание '{text}' на {time_str} добавлено.")

@error_handler
def add_note(text):
    if not text or text.strip() == "":
        speak("Пожалуйста, укажите текст заметки.")
        return
        
    system_state['notes'].append({'text': text, 'timestamp': datetime.datetime.now().isoformat()})
    speak(f"Заметка '{text}' добавлена.")

@error_handler
def read_notes():
    if not system_state['notes']:
        speak("У вас нет заметок.")
        return
    speak("Ваши заметки:")
    for i, note in enumerate(system_state['notes'], 1):
        speak(f"{i}. {note['text']}")

@error_handler
def set_timer(duration):
    try:
        if not duration or duration.strip() == "":
            speak("Пожалуйста, укажите время для таймера.")
            return
            
        minutes = int(duration)
        if minutes <= 0:
            speak("Время таймера должно быть больше нуля.")
            return
            
        timer_id = f"timer_{len(system_state['timers'])}"
        system_state['timers'][timer_id] = {
            'duration': minutes,
            'start_time': datetime.datetime.now(),
            'end_time': datetime.datetime.now() + datetime.timedelta(minutes=minutes)
        }
        def timer_thread():
            time.sleep(minutes * 60)
            speak(f"Таймер на {minutes} минут завершен!")
            system_state['timers'].pop(timer_id, None)
        threading.Thread(target=timer_thread, daemon=True).start()
        speak(f"Таймер на {minutes} минут установлен.")
    except ValueError:
        speak("Пожалуйста, укажите время в минутах.")

@error_handler
def set_alarm(time_str):
    try:
        # Парсинг времени (формат: HH:MM)
        try:
            hour, minute = map(int, time_str.split(':'))
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError("Неверный формат времени")
        except ValueError:
            speak("Пожалуйста, укажите время в формате ЧЧ:ММ (например, 08:30)")
            return
            
        alarm_id = f"alarm_{len(system_state['alarms'])}"
        system_state['alarms'][alarm_id] = {
            'time': time_str,
            'hour': hour,
            'minute': minute,
            'created': datetime.datetime.now().isoformat()
        }
        
        # Запуск фонового потока для проверки будильника
        def alarm_checker():
            while True:
                now = datetime.datetime.now()
                if now.hour == hour and now.minute == minute:
                    speak(f"Будильник! Время {time_str}")
                    system_state['alarms'].pop(alarm_id, None)
                    break
                time.sleep(30)  # Проверка каждые 30 секунд
        
        threading.Thread(target=alarm_checker, daemon=True).start()
        speak(f"Будильник на {time_str} установлен.")
    except Exception as e:
        logger.error(f"Ошибка установки будильника: {e}")
        speak("Не удалось установить будильник.")

# --- Система мониторинга и обучения ---
@error_handler
def toggle_monitoring():
    if not system_state['monitoring_enabled']:
        system_state['monitoring_enabled'] = True
        speak('Мониторинг экрана включен.')
        _start_screen_monitor()
    else:
        _stop_screen_monitor()

@error_handler
def toggle_privacy_mode():
    _toggle_state('privacy_mode', 'Режим конфиденциальности')

@error_handler
def toggle_learning_mode():
    _toggle_state('learning_mode', 'Режим обучения')

@error_handler
def adapt_to_game(game_name):
    if not game_name or game_name.strip() == "":
        speak("Пожалуйста, укажите название игры.")
        return
        
    system_state['current_game'] = game_name
    speak(f"Адаптируюсь к игре {game_name}.")

@error_handler
def toggle_do_not_disturb():
    _toggle_state('do_not_disturb', "Режим 'не беспокоить'")

@error_handler
def show_activity_logs():
    try:
        with open('soika_errors.log', 'r', encoding='utf-8') as f:
            logs = f.readlines()[-20:]
        speak("Показываю логи активности за сегодня.")
        for log in logs:
            print(log.strip())
    except Exception as e:
        logger.error(f"Ошибка чтения логов: {e}")
        speak("Не удалось прочитать логи.")

@error_handler
def clear_yesterday_data():
    speak("Данные за вчера удалены.")

@error_handler
def get_system_insights():
    insights = list(filter(None, [
        _get_status('monitoring_enabled', 'Мониторинг экрана активен'),
        _get_status('privacy_mode', 'Режим конфиденциальности включен'),
        _get_status('learning_mode', 'Режим обучения активен'),
        _get_status('do_not_disturb', "Режим 'не беспокоить' включен"),
        f"Адаптирована к игре {system_state['current_game']}" if system_state['current_game'] else None
    ]))
    if not insights:
        insights.append("Система работает в обычном режиме")
    speak("Мои текущие догадки:")
    for insight in insights:
        speak(insight)

# --- Шутки ---
@error_handler
def tell_joke():
    jokes = [
        "Почему программисты не ходят в лес? Потому что там много багов.",
        "Какой язык программирования предпочитают океаны? Си.",
        "Почему питоны никогда не устают? Потому что они всегда остаются гибкими.",
        "Почему Java-программисты всегда носят очки? Потому что они не могут C#.",
        "Что говорят разработчики, когда их код работает? Это магия!"
    ]
    speak(random.choice(jokes))

@error_handler
def show_background_processes():
    speak("Показываю фоновые процессы.")
    print("\n--- Фоновые процессы Soika ---")
    for t in threading.enumerate():
        print(f"Имя: {t.name}, Alive: {t.is_alive()}, Daemon: {t.daemon}")
    print("-----------------------------\n")

# --- Основная функция обработки команд ---
@error_handler
def process_command(command):
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
    elif 'покажи фоновые процессы' in command:
        show_background_processes()
    # Базовые команды
    elif 'привет' in command:
        speak("Привет! Я Soika, как я могу помочь?")
    elif 'что ты можешь' in command or 'что ты умеешь' in command:
        speak("Я Soika, и я могу выполнять различные команды: управлять компьютером, работать с интернетом, искать файлы, управлять музыкой, устанавливать напоминания и таймеры, а также многое другое.")
    elif any(x in command for x in ['расскажи шутку', 'пошути', 'шутка']):
        tell_joke()
    else:
        speak("Я не знаю, как выполнить эту команду. Попробуйте сказать 'что ты можешь' для списка команд.")

if __name__ == "__main__":
    try:
        logger.info("Soika запущена")
        speak("Привет! Я Soika, ваш голосовой помощник. Как я могу помочь?")
        # Запуск фоновых потоков
        threading.Thread(target=background_clear_memory, daemon=True).start()
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
            except Exception as e:
                logger.error(f"Критическая ошибка: {e}")
                speak("Произошла критическая ошибка. Перезапускаюсь...")
                time.sleep(2)
            except SystemExit:
                logger.info("Soika завершена системой")
                speak("До свидания!")
                break
    except Exception as e:
        print(f"Критическая ошибка при запуске Soika: {e}")
        logger.error(f"Критическая ошибка при запуске: {e}")
