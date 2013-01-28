set terminal png font 14 size 800,400
set xdata time
set timefmt "%Y-%m-%d"

# -- time range must be in same format as data file
set xrange ["2012-12-01":]

set key inside left top vertical
# set grid
# set nokey

set format x "%m/%d"

# -- epoch time, full width = 86400
set mxtics 0
set xtics 345600  # every three days
set boxwidth 50000 absolute    # 86400 = 100%

set style line 1 lt 1 lw 1
set style line 2 lt 3 lw 3 

# set xlabel "Date"
set ylabel "Users" 
set title "DB Class Winter -- Enrolled"
set output "users_by_day.png"
plot "users_by_day.dat" using 1:2 with boxes ls 1 fill solid 0.3 title "new", \
   "" u 1:($2 + 4000):($2) every 3 with labels notitle, \
   "" using 1:2 s cumul ls 2 title "cumulative"

