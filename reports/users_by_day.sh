#!/bin/bash -e

mysql < users_by_day.sql > users_by_day.dat

gnuplot < users_by_day.plot

if [[ $# -eq 1 ]]; then
    echo "mailing graph to $1"
    mpack -s "Class2Go Users by Day Report" users_by_day.png  $1
fi

