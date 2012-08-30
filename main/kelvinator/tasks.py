import subprocess
import os

from celery import task

@task()
def run(path, frames, threshold):
    #local for now
    #target_url="s3://%(bucket)s%(path)s" % target
    mylocation=os.path.dirname(__file__)

    logfile = open("/var/log/django/kelvinator.log", "a")

    subprocess.Popen(
        [mylocation+"/kelvinator.sh", path, str(frames), str(threshold)],
        stdout=logfile, stderr=logfile,
        cwd=mylocation,
    )
