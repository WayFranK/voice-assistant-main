from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class SystemState:
    monitoring_enabled: bool = False
    privacy_mode: bool = False
    learning_mode: bool = False
    do_not_disturb: bool = False
    current_game: Optional[str] = None
    notes: List[Dict[str, Any]] = field(default_factory=list)
    reminders: List[Dict[str, Any]] = field(default_factory=list)
    timers: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    alarms: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    monitor_thread: Optional[Any] = None
    monitor_window: Optional[Any] = None


state = SystemState()


def toggle_flag(flag_name: str) -> bool:
    if not hasattr(state, flag_name):
        raise AttributeError(f"Unknown flag: {flag_name}")
    current = bool(getattr(state, flag_name))
    setattr(state, flag_name, not current)
    return getattr(state, flag_name)


