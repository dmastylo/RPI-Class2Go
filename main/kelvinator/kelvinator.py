import subprocess
import os

def run(target):
    target_url="s3://%(bucket)s%(path)s" % target
    mylocation=os.path.dirname(__file__)

    logfile = open("/var/log/django/kelvinator.log", "a")

    subprocess.Popen(
        [mylocation+"/kelvinator.sh", target_url, str(target['frames']), str(target['threshold'])],
        stdout=logfile, stderr=logfile,
        cwd=mylocation,
    )
