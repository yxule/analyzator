import csv
import time

from psutil import process_iter
from pynput import keyboard, mouse
from threading import Thread, Event, Lock

from config import events, timestamp

f = open(events['FILE'], "w", newline="", encoding="utf-8")
writer = csv.writer(f)
writer.writerow(["version", "timestamp", "event", "type", "data"])

lock = Lock()
stop_event = Event()

VERSION = events['VERSION']
    
def formatting_event_data(event, etype, **kwargs):
    if stop_event.is_set():
        return
    try:
        template: str = events[event][etype]
        data = template.format(**kwargs)
        with lock:
            writer.writerow([VERSION, timestamp(), event, etype, data])
    except Exception as exc:
        print(f'Ошибка форматирования данных: {exc}')

def on_press(key):
    formatting_event_data('KEYBOARD', 'PRESS', key=key)
    if key == keyboard.Key.backspace:
        stop_event.set()
        mouse_listener.stop()
        keyboard_listener.stop()

mouse_listener = mouse.Listener(
    on_move=lambda x, y: formatting_event_data(
        'MOUSE',
        'MOVE',
        x=x,
        y=y
    ),
    on_scroll=lambda x, y, dx, dy: formatting_event_data(
        'MOUSE',
        'SCROLL',
        x=x,
        y=y,
        dx=dx,
        dy=dy
    ),
    on_click=lambda x, y, button, pressed: formatting_event_data(
        'MOUSE',
        'PRESS' if pressed else 'RELEASE',
        x=x,
        y=y,
        b=button.name if hasattr(button, 'name') else str(button)
    )
)
keyboard_listener = keyboard.Listener(
    on_press=on_press,
    on_release=lambda key: formatting_event_data(
        'KEYBOARD',
        'RELEASE',
        key=key
    )
)

def search_process(event = 'PROCESS', etype = 'GET'):
    while not stop_event.is_set():
        processes = []
        # Поиск
        for p in process_iter(attrs=['name', 'memory_percent'], ad_value=0.0):
            name, mem = p.info['name'], p.info['memory_percent']
            # Системные процессы
            if name in ['MemCompression', ...]:
                continue
            processes.append((name, mem))
        # Сортировка
        sorted_processes = sorted(processes, key=lambda x: x[1], reverse=True)
        names = []
        # Дубликаты
        for item in sorted_processes:
            if item[0] not in names:
                names.append(item[0])
        # Обрезка и заполнение
        names = names[:3]
        while len(names) < 3:
            names.append('')
        # Форматирование
        data = ':'.join(names)
        with lock:
            writer.writerow([VERSION, timestamp(), event, etype, data])
        # Цикл
        time.sleep(1)

process_timer = Thread(target=search_process)

# Запуск
print(f"Файл: {events['FILE']}")
mouse_listener.start()
keyboard_listener.start()
process_timer.start()
# После остановки слушателей
keyboard_listener.join()
mouse_listener.join()
process_timer.join()

f.close()
print("Логирование завершено.")