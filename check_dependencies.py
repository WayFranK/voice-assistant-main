#!/usr/bin/env python3
"""
Скрипт для проверки зависимостей Soika
"""

import sys
import importlib

def check_dependency(module_name, package_name=None):
    """Проверяет, установлен ли модуль"""
    try:
        importlib.import_module(module_name)
        print(f"✓ {package_name or module_name} установлен")
        return True
    except ImportError:
        print(f"✗ {package_name or module_name} НЕ установлен")
        return False

def main():
    print("Проверка зависимостей для Soika...")
    print("=" * 40)
    
    dependencies = [
        ("speech_recognition", "SpeechRecognition"),
        ("pyttsx3", "pyttsx3"),
        ("psutil", "psutil"),
        ("PIL", "Pillow"),
        ("pyautogui", "pyautogui"),
        ("pyaudio", "PyAudio"),
    ]
    
    missing = []
    for module, package in dependencies:
        if not check_dependency(module, package):
            missing.append(package)
    
    print("=" * 40)
    
    if missing:
        print(f"\nОтсутствуют зависимости: {', '.join(missing)}")
        print("Установите их командой:")
        print(f"pip install {' '.join(missing)}")
        return False
    else:
        print("\nВсе зависимости установлены! Soika готова к запуску.")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
