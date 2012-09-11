#!/bin/bash
#
# Set up symlinks from shared directory. Assumes being run in the users 
# own class2go/chef dir
#

SHARE="/home/shared"
CHEF="/home/shared/class2go/chef"

CD=`pwd`
if [[ ${CD:(-14)} != "/class2go/chef" ]]; then
    echo "not in the \"class2go/chef\" directory, quitting to stay safe"
    exit 1
fi

for file in `(cd $CHEF; find . -type f)`; do
    rel=${file/.\//}
    ln -v -n -s $CHEF/$rel $rel
done

