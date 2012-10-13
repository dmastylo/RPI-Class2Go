#!/bin/bash

# Note: I had to do some permissions hacking to be able to send mail from my mac
# see this thread: https://discussions.apple.com/thread/4136501?start=0&tstart=0

. ./bash_bug_reports.sh

TODAY=`date +"%A %D"`
buglist-full-report | mail -s "Class2Go Bug Summary - ${TODAY}" c2g-dev@cs.stanford.edu,mitchell@cs.stanford.edu

