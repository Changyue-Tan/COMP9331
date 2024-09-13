echo -----------------------------------
echo -'sending ICMP echo request to google.com'
echo -----------------------------------

ping google.com
# send continuous stream of 
# Internet Control Message Protocol (ICMP) 
# echo request packets and wait for an ICMP echo reply
# helps diagnose network issues by measuring round-trip time and packet loss

echo -----------------------------------
echo -'sending 4 packets only'
echo -----------------------------------

ping -c 4 google.com

echo -----------------------------------
echo -'send packets of size 100 bytes'
echo -----------------------------------

ping -s 100 google.com
# defult 64 bytes contating 56 data bytes an 8 bytes of protocol header information

echo -----------------------------------
echo -'send packets at an interval of 2 seconds'
echo -----------------------------------

ping -i 2 google.com
# default 1 second

# Time To Live (TTL): limits the lifespan of the packet 
