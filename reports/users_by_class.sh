#!/bin/bash -e

mysql -N < users_by_class.sql > users_by_class.dat

gnuplot < users_by_class.plot

if [[ $# -eq 1 ]]; then
    echo "mailing graph to $1"
    mpack -s "Class2Go Users by Class Report" users_by_class.png $1
fi

