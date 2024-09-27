#coding: utf-8
import socket
import sys
import time
import random
import statistics

# Get command-line arguments
args = sys.argv

host = args[1]
port = int(args[2])

# serverName = 'localhost'
serverName = host
serverPort = port

# create socket
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# set a time out time 0.6 seconds
clientSocket.settimeout(0.6)

num_pings = 15
successful_pings = 0
start_time = time.time()
rtts = []

# create a start of sequence number 
seq_num = random.randint(10000, 20000)

for _ in range(num_pings):

    message = f"PING {seq_num} {time.time()}"
    seq_num += 1

    try:
        # Send the ping request
        clientSocket.sendto(message.encode(), (host, port))
        sent_time = time.time()

        # Wait for a response
        _, _ = clientSocket.recvfrom(2048)
        rtt = (time.time() - sent_time) * 1000  # RTT in milliseconds
        
        print(f"PING to {host}, seq={seq_num}, RTT={rtt:.3f} ms")
        rtts.append(rtt)
        successful_pings += 1

    except socket.timeout:
        print(f"PING to {host}, seq={seq_num}, RTT=timeout ms")

# record end time
end_time = time.time()
    
# Calculate statistics
total_time = end_time - start_time
packet_loss = num_pings - successful_pings
percentage_loss = (packet_loss / num_pings) * 100

if successful_pings > 0:
    min_rtt = min(rtts)
    max_rtt = max(rtts)
    avg_rtt = sum(rtts) / successful_pings
    jitter = statistics.variance(rtts) ** 0.5 if successful_pings > 1 else 0
else:
    min_rtt = max_rtt = avg_rtt = jitter = 0

# Report statistics

print("Total packets sent: 15")
print(f"Packets acknowledged: {successful_pings}")
print(f"Packet loss: {percentage_loss:.0f}%")
print(f"Minimum RTT: {min_rtt:.0f} ms, Maximum RTT: {max_rtt:.0f} ms, Average RTT: {avg_rtt:.0f} ms")
print(f"Total transmission time: {total_time} ms")
print(f"Jitter: {jitter:.0f} ms")


clientSocket.close()
