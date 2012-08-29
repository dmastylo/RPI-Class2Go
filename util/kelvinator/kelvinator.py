import subprocess
import os

def run(target):
    target_url="s3://%(bucket)s%(path)s" % target
    mylocation=os.path.dirname(__file__)
    subprocess.Popen(
        [mylocation+"/kelvinator.sh", target_url, str(target['frames']), str(target['threshold'])],
        cwd=mylocation,
    )
