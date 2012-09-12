1. On a prod machine: 
    echo "select date(date_joined), count(*) from auth_user group by 1;" | ~/class2go/main/manage.py dbshell

2. Copy/paste into the file on your machine
    ./users_by_day.dat

3. Run this command:
    cat plot_users.conf | gnuplot

4. Total?
    cat users_by_day.dat | awk '{x += $2} END {print x}'

The chart will be in class2go_users.png
