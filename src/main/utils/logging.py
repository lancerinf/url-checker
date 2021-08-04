from datetime import datetime


def log_message(msg):
    print(f"{datetime.now():%Y-%m-%d %H:%M} - {msg}")
