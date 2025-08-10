from __future__ import annotations

import os

from ..speech import speak
from ..utils import error_handler


@error_handler
def control_music(action: str) -> None:
    if not action or action.strip() == "":
        speak("Пожалуйста, укажите действие для управления музыкой.")
        return
    actions = {
        'play':   ("start wmplayer", "Включаю проигрыватель Windows Media."),
        'pause':  ("powershell (New-Object -ComObject WScript.Shell).SendKeys([char]179)", "Ставлю музыку на паузу."),
        'next':   ("powershell (New-Object -ComObject WScript.Shell).SendKeys([char]176)", "Следующий трек."),
        'volume_up': ("powershell (New-Object -ComObject WScript.Shell).SendKeys([char]175)", "Увеличиваю громкость."),
        'volume_down': ("powershell (New-Object -ComObject WScript.Shell).SendKeys([char]174)", "Уменьшаю громкость."),
    }
    cmd, msg = actions.get(action, (None, None))
    if cmd:
        os.system(cmd)
        speak(msg)
    else:
        speak("Неизвестное действие для управления музыкой.")


