from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv
load_dotenv("../.env")
import os
import tasks.helper as helper
import tasks.celeryconfig as celeryconfig

app = Celery('tasks', broker='redis://redis:6379/0')

app.conf.broker_url = celeryconfig.broker_url
app.conf.result_backend = celeryconfig.result_backend

# for database connection
app.env_vars = {
    'MYSQL_PORT':  int(os.getenv("DOCKER_MYSQL_PORT",os.getenv("MYSQL_PORT", "3306"))),
    'MYSQL_HOST':  os.getenv("DOCKER_MYSQL_HOST",os.getenv("MYSQL_HOST", "localhost")),
    'MYSQL_USER':  os.getenv("DOCKER_MYSQL_USER",os.getenv("MYSQL_USER", "root")),
    'MYSQL_PASSWORD':  os.getenv("DOCKER_MYSQL_PASSWORD",os.getenv("MYSQL_PASSWORD", "root")),
    'MYSQL_DB':  os.getenv("DOCKER_MYSQL_DB",os.getenv("MYSQL_DB", "kanver")),
}

@app.task(name="tasks.print_hello")
def print_hello():
    print("Hello, this task runs periodically!")
@app.task(name="tasks.query_now_eligble_users")
def query_now_eligble_users():
    for users in helper.get_users_that_needs_update(app.env_vars, batch_size=100):
        print(f"queried now eligble {len(users)} users")   
        update_eligibility.delay(users)
@app.task(name="tasks.update_eligibility")
def update_eligibility(users):
    print(f"updating eligibilty for {len(users)} users")   
    helper.update_users_to_set_eligiblity(app.env_vars, users)
    send_emails_for_eligiblty.delay(users)
@app.task(name="send_emails_for_eligiblty")
def send_emails_for_eligiblty(users):
    #  send_emails(users, template_id = ?)
    print(f"sending emails for {len(users)} users") 

app.conf.beat_schedule = {
    'say-hello-every-10-seconds': {
        'task': 'tasks.print_hello',
        'schedule': 10.0,  # Every 10 seconds
    },
    'connect-to-database-every-10-seconds': {
        'task': 'tasks.query_now_eligble_users',
        'schedule': 10.0,  # Every 10 seconds
    },
}
app.conf.timezone = 'UTC'
