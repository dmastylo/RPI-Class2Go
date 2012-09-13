from django.core.management.base import BaseCommand, CommandError
from c2g.models import *
from django.contrib.auth.models import User,Group
from django.db import connection, transaction
from kelvinator import kelvinator
from database import AWS_STORAGE_BUCKET_NAME
import urllib, urllib2

class Command(BaseCommand):
    help = "Runs the Kelvinator on a video given its slug.\nUsage:\n     1. manage kelvinate <video_slug>\n     2. manage kelvinate <video_slug> <keyframes per minute>\n"
        
    def handle(self, *args, **options):
        if len(args) == 0:
            print "No video slug supplied!"
            
        try:
            video = Video.objects.get(slug= args[0], mode='draft')
        except:
            print "Failed to find video with given slug"
            return
            
        s3_path="https://s3-us-west-2.amazonaws.com/"+AWS_STORAGE_BUCKET_NAME+"/"+urllib.quote_plus(video.file.name,"/")
        
        keyframes_per_minute = 2
        if len(args) > 1:
            keyframes_per_minute = args[1]
        
        report = kelvinator.run(s3_path, keyframes_per_minute)
        
        print "Kelvination complete."
        print "---------------------"
        print report