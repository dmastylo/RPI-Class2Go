set terminal png font 14 size 600,400
set output "users_by_class.png"

set nokey

set boxwidth .5

set ylabel "Users" 
set title "Class2Go Users"
plot "users_by_class.dat" using 2:xticlabels(1) with boxes fill solid 0.3
