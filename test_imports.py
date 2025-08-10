#!/usr/bin/env python3
"""
Скрипт для проверки всех импортов проекта Soika
"""

def test_imports():
    """Проверяет все необходимые импорты"""
    imports = [
        'speech_recognition',
        'pyttsx3', 
        'psutil',
        'PIL',
        'pyautogui',
        'tkinter',
        'threading',
        'datetime',
        'logging',
        'pathlib',
        'urllib.parse',
        'webbrowser',
        'subprocess',
        'os',
        'time',
        'random'
    ]
    
    failed_imports = []
    
    for module in imports:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Не удалось импортировать: {', '.join(failed_imports)}")
        return False
    else:
        print("\n✅ Все импорты успешны!")
        return True

if __name__ == "__main__":
    print("Проверка импортов для Soika...")
    print("=" * 40)
    success = test_imports()
    print("=" * 40)
    
    if success:
        print("🎉 Все готово для запуска Soika!")
    else:
        print("⚠️  Установите недостающие зависимости:")
        print("pip install -r requirements.txt")
