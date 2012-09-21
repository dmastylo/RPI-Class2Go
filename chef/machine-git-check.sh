#!/bin/bash -e
#
# For an environment (prod, stage, etc) find all the servers, for those servers show
# 1. output of "git status" and
# 2. most recent change -- ie what is checked out on that machine
#

if [[ $# == 0 ]]; then
    env=prod
else
    env=$1
fi

knife ssh -C 1 -Ft "name:app*.${env}" -x bitnami '(cd ~/class2go; git status; git log -1)' -a fqdn
knife ssh -C 1 -Ft "name:util*.${env}" -x ubuntu '(cd ~/class2go; git status; git log -1)' -a fqdn

