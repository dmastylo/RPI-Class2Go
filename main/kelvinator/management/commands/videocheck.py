#!/usr/bin/env python
#
# note total_ordering makes this Python 2.7 dependent.
#

import os
import time
import urllib
import re
import boto
from functools import total_ordering

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from optparse import make_option

import kelvinator.tasks
from c2g.models import Video
from c2g.readonly import use_readonly_database

class Command(BaseCommand):
    help = """    Audit videos to see what commands need to be run to fix them
    out.  Looks out for missing thumbnails or smaller video files.
    Does this by comparing contents of database to what is in S3.
    Note that this doesn't do any *semantic* validation, just checks
    for presence of files.  For example, doesn't tell if they are
    good thumbnails, or even the right thumbnails, just that there
    are thumbnails.

    Output is a set of commands to be run to fix it up.
    """

    option_list = (
        # Main options
        make_option("-c", "--class", dest="class",
            help="restrict to class name, any term eg \"cs144\""),
        make_option("-t", "--term", dest="term",
            help="restrict to term, any class eg \"Fall2012\""),

        make_option("-q", "--quiet", dest="quiet", action="store_true",
                    help="don't print helpful warnings or summary info (still prints video names)"), 
    ) + BaseCommand.option_list


    @use_readonly_database
    def handle(self, *args, **options):

        @total_ordering
        class FoundVideo(object):
            """
            Simple class to store info about videos.  For identity and comparison, we use
            {prefix,suffix,video_id}.  But the params() command prints slug, since that's
            what's used for further commands.
            """

            def __init__(self, prefix, suffix, video_id, slug=None, file=None):
                self.prefix = str(prefix)
                self.suffix = str(suffix)
                self.video_id = str(video_id)
                self.slug = str(slug)
                if file != None:
                    self.file = str(file)

            def __eq__(self, other):
                return self.prefix == other.prefix \
                    and self.suffix == other.suffix \
                    and self.video_id == other.video_id

            def __lt__(self, other):
                return self.prefix < other.prefix \
                    and self.suffix < other.suffix \
                    and self.video_id < self.video_id

            def __hash__(self):
                return hash((self.prefix, self.suffix, self.video_id))

            def __str__(self):
                return "%s %s %s %s %s" % (self.prefix, self.suffix, self.video_id, self.slug, self.file)

            def fixup_params(self):
                return "%s %s %s" % (self.prefix, self.suffix, self.slug)

        def searchDatabase(limitClass=None, limitTerm=None):
            """
            Search the database and return the set of FoundVideo objects that we should
            consider when looking for problems. Optionally limit by course or by term
            (or both).  Limits are case insensitive.
            """
            if limitClass != None and limitTerm != None:
                limit = "%s--%s" %(limitClass, limitTerm)
                videosInDB = Video.objects.filter(is_deleted=0,mode="draft", course__handle__iexact=limit)
            elif limitClass != None:
                limit = "%s--" % limitClass
                videosInDB = Video.objects.filter(is_deleted=0,mode="draft", course__handle__istartswith=limit)
            elif limitTerm != None:
                limit = "--%s" % limitTerm
                videosInDB = Video.objects.filter(is_deleted=0,mode="draft", course__handle__iendswith=limit)
            else:
                videosInDB = Video.objects.filter(is_deleted=0,mode="draft")

            foundVideos=set([])
            for v in videosInDB:
                fv = FoundVideo(v.course.prefix, v.course.suffix, v.id, v.slug, v.file)
                foundVideos.add(fv)

            return foundVideos


        def searchStorage(awsKey, awsSecret, awsBucket, limitClass=None, limitTerm=None):
            """
            Search the S3 storage bucket to see what videos are.  Returns a bunch of sets
            for what's found in there:
               videos
               manifests -- proxy for existence of thumbnails
               small -- small size 
               large -- large / normal size 
            FoundVideo objects.  Optionally limit by course name, term, or both.

            Contents of S3 look like this: 
               nlp/Fall2012/videos/39/intro.m4v
               nlp/Fall2012/videos/39/small/intro.m4v
               nlp/Fall2012/videos/39/large/intro.m4v
               nlp/Fall2012/videos/39/jpegs/manifest.txt
            """
            store_contents=[]
            if awsKey == "local" or awsSecret == "local":
                media_root = getattr(settings, 'MEDIA_ROOT')
                for (path, dirs, files) in os.walk(media_root):
                    for f in files:
                        p=os.path.join(path, f)
                        if p.startswith(media_root + "/"):
                            p = p[len(media_root)+1:]
                        store_contents.append(p)
            else:
                conn=boto.connect_s3(awsKey, awsSecret)
                bucket_conn=conn.get_bucket(awsBucket)
                store_contents_s3=bucket_conn.list()
                store_contents=map(lambda x: x.name, store_contents_s3)

            def filterStoragePaths(paths, regexp):
                """
                Return set of FoundVideos for all paths matching regexp.  Expect RE has four 
                match sections: prefix, suffix, video_id, filename
                """
                foundSet=set([])
                path_regexp=re.compile(regexp)
                for store_entry in store_contents:
                    match = path_regexp.match(store_entry)
                    if match:
                        fv = FoundVideo(prefix=match.group(1),
                                        suffix=match.group(2),
                                        video_id=match.group(3),
                                        file=match.group(4))
                        if limitClass and limitClass.lower() != fv.prefix.lower():
                            next
                        if limitTerm and limitTerm.lower() != fv.suffix.lower():
                            next
                        foundSet.add(fv)
                return foundSet

            # remember that video regexp'es need to handle spaces in file names
            foundVideos = filterStoragePaths(store_contents, 
                    r"(\w*)/(\w*)/videos/(\w*)/([^/]+)$")
            foundManifests = filterStoragePaths(store_contents, 
                    r"(\w*)/(\w*)/videos/(\w*)/jpegs/(manifest.txt)$")   # dummy filename
            foundSmalls = filterStoragePaths(store_contents, 
                    r"(\w*)/(\w*)/videos/(\w*)/small/([^/]+)$")
            foundLarges = filterStoragePaths(store_contents, 
                    r"(\w*)/(\w*)/videos/(\w*)/large/([^/]+)$")

            return (foundVideos, foundManifests, foundSmalls, foundLarges)


        ## MAIN

        dbVideoSet=searchDatabase(options['class'], options['term'])
        if not options['quiet']: 
            print "Videos found in database: %d " % len(dbVideoSet)

        awsKey=getattr(settings, 'AWS_ACCESS_KEY_ID')
        awsSecret=getattr(settings, 'AWS_SECRET_ACCESS_KEY')
        awsBucket=getattr(settings, 'AWS_STORAGE_BUCKET_NAME')

        (storeVideoSet, storeManifestSet, storeSmallSet, storeLargeSet) = \
                searchStorage(awsKey, awsSecret, awsBucket, options['class'], options['term'])
        if not options['quiet']: 
            print "Bucket: " + awsBucket
            print "\tvideos found: %d" % len(storeVideoSet)
            print "\tmanifests found: %d" % len(storeManifestSet)
            print "\tsmall formats found: %d" % len(storeSmallSet)
            print "\tlarge formats found: %d" % len(storeLargeSet)

        missingVideoSet = dbVideoSet.difference(storeVideoSet)
        missingThumbSet = dbVideoSet.difference(missingVideoSet).difference(storeManifestSet)
        missingSmallSet = dbVideoSet.difference(missingVideoSet).difference(storeSmallSet)
        missingLargeSet = dbVideoSet.difference(missingVideoSet).difference(storeLargeSet)
        if not options['quiet']: 
            print "in database, but not in storage: %d" % len(missingVideoSet)
            print "in database and storage, but no thumbnails: %d" % len(missingThumbSet)
            print "in database and storage, but no small format: %d" % len(missingSmallSet)
            print "in database and storage, but no large format: %d" % len(missingSmallSet)
            print "=================================="

        problems = sorted(missingThumbSet.union(missingSmallSet).union(missingLargeSet))
        for p in problems:
            if p in missingThumbSet:
                print "./manage.py kelvinate %s     # id=%s file=%s" \
                        % (p.fixup_params(), p.video_id, p.file)
            if p in missingSmallSet:
                print "./manage.py resize small %s    # id=%s file=%s" \
                        % (p.fixup_params(), p.video_id, p.file)
            if p in missingLargeSet:
                print "./manage.py resize large %s    # id=%s file=%s" \
                        % (p.fixup_params(), p.video_id, p.file)

        for m in missingVideoSet:
            print "# missing video file \"%s\" for %s, id=%s" \
                    % (m.file, m.fixup_params(), m.video_id)

