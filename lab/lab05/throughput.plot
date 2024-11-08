set xlabel "time [s]"
set ylabel "Throughput [Mbps]"
set key bel
plot  "tcp1.tr" t "TCP1" w lp, "tcp2.tr" t "TCP2" w lp
pause -1