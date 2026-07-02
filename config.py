from pathlib import Path
from datetime import datetime

LOG_DIR = Path('logs')
LOG_DIR.mkdir(exist_ok=True)

SESSION_ID = datetime.now().strftime('%Y%m%d_%H%M%S')
FILE = LOG_DIR / f'session_{SESSION_ID}.csv'

events = {
    'FILE': FILE,
    'VERSION': 'v1.1',
    'TIMESTAMP_FORMAT': '%d.%m.%y-%H:%M:%S.%f',
    'MOUSE': {
        'MOVE': '{x}:{y}',
        'SCROLL': '{dx}:{dy}',
        'PRESS': '{x}:{y}:{b}',
        'RELEASE': '{x}:{y}:{b}'
    },
    'KEYBOARD': {
        'PRESS': '0',
        'RELEASE': '1'
    },
    'PROCESS': {
        'GET': '{n}_1:{n}_2:{n}_3'
    }
}
def timestamp(TIMESTAMP_FORMAT = events['TIMESTAMP_FORMAT']) -> str:
    result = datetime.now().strftime(TIMESTAMP_FORMAT)
    return result