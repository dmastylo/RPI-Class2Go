#!/bin/bash

# Note: I had to do some permissions hacking to be able to send mail from my mac
# see this thread: https://discussions.apple.com/thread/4136501?start=0&tstart=0

. ./bash_aliases

TODAY=`date +"%A %D"`
buglist-goalline | mail -s "Sophi Bug Summary - ${TODAY}" sophi-dev@cs.stanford.edu,mitchell@cs.stanford.edu

