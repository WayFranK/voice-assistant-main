from __future__ import annotations

from functools import wraps
import logging
from typing import Any, Callable, Optional, TypeVar, cast

from .speech import speak


logger = logging.getLogger("soika")
F = TypeVar("F", bound=Callable[..., Any])


def error_handler(func: F) -> F:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any):  # type: ignore[misc]
        try:
            return func(*args, **kwargs)
        except Exception as exc:  # pragma: no cover
            logger.error(f"Ошибка в функции {func.__name__}: {exc}")
            speak("Произошла ошибка при выполнении команды. Попробуйте еще раз.")
            return None
    return cast(F, wrapper)


