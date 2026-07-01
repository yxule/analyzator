import csv

import time
from threading import Thread

from datetime import datetime
from pathlib import Path

from psutil import process_iter
from pynput import keyboard, mouse

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
SESSION_ID = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE = LOG_DIR / f"session_{SESSION_ID}.csv"

# поля csv
# version, timestamp, event, type, data
# файл для записи
f = open(LOG_FILE, "w", newline="", encoding="utf-8")
writer = csv.writer(f)
writer.writerow(["version", "timestamp", "event", "type", "data"])

version = 'v1'
stop_flag = False

# --- Обработчики мыши ---
def on_move(x, y):
    if stop_flag:
        return False
    writer.writerow([
        version, datetime.now().strftime('%d.%m.%y-%H:%M:%S.%f'),
        'mouse', 'move', f'%{x}:%{y}'
    ])

def on_scroll(x, y, dx, dy):
    if stop_flag:
        return False
    writer.writerow([
        version, datetime.now().strftime('%d.%m.%y-%H:%M:%S.%f'),
        'mouse', 'scroll', f'%{dx}:%{dy}'
    ])

def on_click(x, y, button, pressed):
    if stop_flag:
        return False
    # Определяем название кнопки
    btn_name = str(button).split(".")[-1]  # left, right, middle
    action = "press" if pressed else "release"
    writer.writerow([
        version, datetime.now().strftime('%d.%m.%y-%H:%M:%S.%f'),
        'mouse', action, f'%{x}:%{y}:%{btn_name}'
    ])

# --- Обработчики клавиатуры ---
def on_press(key):
    if stop_flag:
        return False
    # Определяем тип клавиши
    if hasattr(key, 'char') and key.char is not None:
        # Обычная клавиша — сохраняем только роль (буква/цифра)
        if key.char.isprintable():
            key_name = "char"  # не пишем сам символ
        else:
            key_name = "other"
    else:
        # Специальные клавиши (Shift, Ctrl, Esc и т.д.)
        key_name = str(key).split(".")[-1] if hasattr(key, 'name') else "special"
        # Фильтруем системные шумы (например, клавиша 160)
        if key_name in ["cmd", "alt", "ctrl", "shift", "esc", "space", "enter", "tab", "backspace", "delete", "up", "down", "left", "right"]:
            pass
        else:
            key_name = "other"
    writer.writerow([
        version, datetime.now().strftime('%d.%m.%y-%H:%M:%S.%f'), 'keyboard', 'press', f'%{key_name}'
    ])

def on_release(key):
    global stop_flag
    if stop_flag:
        return False
    
    if key == keyboard.Key.backspace:
        stop_flag = True
        return False
    
    writer.writerow([version, datetime.now().strftime('%d.%m.%y-%H:%M:%S.%f'), 'keyboard', 'release', '%b'])

def search_proccess():
    while not stop_flag:
        pr = []
        for p in process_iter(attrs=['name']):
            pr.append(p.info['name'])
            if len(pr) == 3:
                break
        print(pr)
        pr = ':%'.join(pr).removeprefix(':')
        writer.writerow([version, datetime.now().strftime('%d.%m.%y-%H:%M:%S.%f'), 'proccess', 'get', pr])
        time.sleep(1)

print(f"Файл: {LOG_FILE}")

mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)
keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
proccess_timer = Thread(target=search_proccess)

mouse_listener.start()
keyboard_listener.start()
proccess_timer.start()

# Ждём, пока не будет остановки
keyboard_listener.join()
mouse_listener.stop()
mouse_listener.join()
proccess_timer.join()

f.close()
print("Логирование завершено.")
