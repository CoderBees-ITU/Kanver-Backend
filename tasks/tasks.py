# tasks/tasks.py
from . import app  # Bu, __init__.py'deki app'i getirir

@app.task(name="tasks.add_numbers")
def add_numbers(x, y):
    return x + y

@app.task(name="tasks.print_message")
def print_message():
    print("Bu bir Celery görevidir!")
