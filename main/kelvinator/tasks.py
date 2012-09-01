import subprocess
import os

from celery import task

@task()
def run(path, frames, threshold):
    mylocation=os.path.dirname(__file__)
    logfile = open("/var/log/django/kelvinator.log", "a")

    subprocess.Popen(
        [mylocation+"/kelvinator.sh", path, str(frames), str(threshold)],
        stdout=logfile, stderr=logfile,
        cwd=mylocation,
    )

