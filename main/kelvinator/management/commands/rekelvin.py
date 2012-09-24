#!/usr/bin/env python

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from optparse import make_option
import boto
import os
import time
import urllib
import re
import kelvinator.tasks

bucket=getattr(settings, 'AWS_STORAGE_BUCKET_NAME')
instance=getattr(settings, 'INSTANCE')

class Command(BaseCommand):
    help = "Look through the S3 bucket to find videos that are missing thumbnails.\n" + \
            "Can also kick off re-kelvinate jobs (local or remote) for the ones\n" + \
            "missing."

    option_list = (
        # Main options
        make_option("-c", "--class", dest="course_prefix",
                    help="restrict to course prefix, like \"cs144\" or \"nlp\""),
        make_option("-q", "--quiet", dest="quiet", action="store_true",
                    help="don't print helpful warnings or summary info (still prints video names)"), 

        # Options for kicking off Kelvination
        make_option("-l", "--local", dest="local", action="store_true",
                    help="do kelvination locally (incompatible with -r)"),
        make_option("-r", "--remote", dest="remote", action="store_true",
                    help="do kelvination remotely (incompatible with -l)"),
        make_option("-m", "--max", dest="max", type="int", default=100000,
                    help="Max number of to kick off"),
        make_option("-d", "--delay", dest="delay", default=0, type="int",
                    help="Seconds to sleep between initiating jobs"),
        make_option("-f", "--frames", dest="target_frames", default=2, type="int",
                    help="Target number of thumbnails per minute (default=2)"),
    ) + BaseCommand.option_list



    def handle(self, *args, **options):

        def search_s3():
            conn=boto.connect_s3()
            bucket_conn=conn.get_bucket(bucket)
            contents_set=bucket_conn.list(options['course_prefix'])

            # example: u'nlp/Fall2012/videos/39/jpegs/manifest.txt'
            # video regexp has to handle spaces in video name
            video_re=re.compile(r"(\w*/\w*/videos/\w*)/[^/]+$")
            manifest_re=re.compile(r"(\w*/\w*/videos/\w*)/jpegs/manifest.txt$")

            videos={}        # dict: first part of path (up to video id), full S3 path 
            videos_skip=[]   # list: ID's of videos with errors to skip

            # scan for all videos
            for path_result in contents_set:
                path = path_result.name
                match = video_re.match(path)
                if match:
                    key = match.group(1)
                    if key in videos:
                        if not options['quiet']:
                            print("WARNING: duplicate videos found, discarding: " + key)
                            print("    " + videos[key])
                            print("    " + path)
                        videos_skip.append(key)
                        next
                    videos[key] = path

            # remove videos that have manifests
            for path_result in contents_set:
                path = path_result.name
                match = manifest_re.match(path)
                if match:
                    key = match.group(1)
                    if key in videos: videos.pop(key)

            # remove dups (may have alrady been removed if one of the dups had a manifest)
            for key in videos_skip:
                if key in videos: videos.pop(key)

            paths=videos.values()
            paths.sort()   # in place
            return paths


        def kickoff(missing):
            upto = min(options['max'], len(missing))
            for i in range(upto):
                if i>0: time.sleep(options['delay'])
                
                m=missing[i]
                s3_path="https://s3-us-west-2.amazonaws.com/"+bucket+"/"+urllib.quote_plus(m,"/")

                if options['local']:
                    print "%d/%d: kelvinating: %s" % (i+1, upto, s3_path)
                    kelvinator.tasks.kelvinate(s3_path, options['target_frames'])
                if options['remote']:
                    print "%d/%d: queueing remote kelvinator (%s): %s" \
                                % (i+1, upto, instance, s3_path)
                    kelvinator.tasks.kelvinate.delay(s3_path, options['target_frames'])
            return


        # Handle Main

        if options['local'] and options['remote']: 
            parser.error("options -l and -r are mutually exclusive")
            return

        if not options['quiet']: print "Bucket: " + bucket
        missing = search_s3()
        if not options['quiet']: print "Total missing slides: %d" % len(missing) 

        if options['local'] or options['remote']: 
            kickoff(missing)
        else:
            for v in missing: print v

