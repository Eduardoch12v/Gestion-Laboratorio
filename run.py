import os
import threading
import webview
from django.core.management import execute_from_command_line

def run_django():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinica.settings')
    execute_from_command_line([
        'manage.py',
        'runserver',
        '127.0.0.1:8000',
        '--noreload'
    ])

def start():
    threading.Thread(target=run_django).start()

    import time
    time.sleep(2)

    webview.create_window("Laboratorio Clínico", "http://127.0.0.1:8000")
    webview.start()

if __name__ == '__main__':
    start()