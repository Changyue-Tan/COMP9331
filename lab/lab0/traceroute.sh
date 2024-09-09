echo ---'tracerouting to google.com'---

traceroute google.com

# a sequence of 
# User Datagram Protocal (UDP) datatram (default 40 bytes)
# is sent to an invalid port address at the remote host

# 3 datagram are sent with 
# Time To Live (TTL) of 1
# makes the datagram to timeout when hit first router on the path to remote host
# the router responds with a
# ICMP Time Exceeded Message (TEM) indicating datagram's expiratio

# 3 datagrams are sent with TTL of 2
# ...
# ICMP Port Unreachable Message is returned at destination