import subprocess
import os

from celery import task
from settings import LOGGING_DIR
from settings import AWS_STORAGE_BUCKET_NAME
@task()
def run(video, kfpm):
    mylocation=os.path.dirname(__file__)
    logfile = open(LOGGING_DIR + "kelvinator.log", "a")

    s3_path = s3_path="https://s3-us-west-2.amazonaws.com/" + AWS_STORAGE_BUCKET_NAME + "/" + urllib.quote_plus(video.file.name,"/")
    
    subprocess.Popen(
        ["python", mylocation+'/kelvinator.py', s3_path, str(kfpm)],
        stdout=logfile, stderr=logfile,
        cwd=mylocation,
    )

