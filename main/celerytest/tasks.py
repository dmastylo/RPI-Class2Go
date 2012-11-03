import time
from celery import task

@task()
def add(x, y):
    return x + y

@task()
def echo(v, t):
    """return value v after sleeping for t seconds"""
    time.sleep(t)
    return v

@task()
def echo_long(v, t):
    """return value v after sleeping for t seconds"""
    time.sleep(t)
    return v
