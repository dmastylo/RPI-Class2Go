import subprocess

def run(target):
    target_url="s3://%(bucket)s%(path)s" % target

    subprocess.call(["kelvinator/kelvinator.sh", 
            target_url, 
            str(target['frames']), 
            str(target['threshold']),
        ])
            
