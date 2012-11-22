#!/bin/bash -e

mysql -N < networking_activity.sql > networking_activity.dat

gnuplot < networking_activity.plot

if [[ $# -eq 1 ]]; then
    echo "mailing graph to $1"
    mpack -s "Networking Activity Graph" networking_activty.png $1
fi

