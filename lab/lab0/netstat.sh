netstat 
# show all active network connecetions

netstat -l
# show services or applications that are currently listening on network ports (TCP and UDP)

netstat -t 
# list all active TCP connetions

netstat -u
# list all active UDP connetions

sudo netstat -p
# show the process identifier (PID) and the name of the program
# that owns each connection or socket

netstat -r
# dispaly system's routing table

netstat -i
# shows statistics such as the 
# number of packets transmitted and received on each network interface.

netstat -s
# show a summary of all network protocols (TCP, UDP, ICMP, etc.) with their statistics

netstat -c
# continuously display network information, updating every second