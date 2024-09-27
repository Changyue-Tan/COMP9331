import socket
import sys
import time
import random

# Get command-line arguments
args = sys.argv
host = args[1]      # host is a string ("127.0.0.1" or "localhost")
port = int(args[2]) # port is a number
serverName = host
serverPort = port

# create socket
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# set a time out time 0.6 seconds
clientSocket.settimeout(0.6)

# initialise variables
num_pings = 15
successful_pings = 0
start_time = time.time() # in seconds
rtts = []

# create a start of sequence number 
seq_num = random.randint(10000, 20000)

# loop to send pings
for _ in range(num_pings):

    # intialise message for each ping
    message = f"PING {seq_num} {time.time()}"
    # increment the sequence number for each ping
    seq_num += 1

    # Send the ping request
    clientSocket.sendto(message.encode(), (host, port))
    # record the time it was sent
    sent_time = time.time()
    
    # try to listen for a response
    try:
        _, _ = clientSocket.recvfrom(1024)
        rtt = (time.time() - sent_time) * 1000  # RTT in milliseconds
        
        print(f"PING to {host}, seq={seq_num}, rtt={rtt:.0f} ms")
        rtts.append(rtt)
        successful_pings += 1

    except socket.timeout:
        print(f"PING to {host}, seq={seq_num}, rtt=timeout")

# record end time
end_time = time.time()

# double check
assert len(rtts) == successful_pings

# Calculate statistics
total_time = end_time - start_time
packet_loss = num_pings - successful_pings
percentage_loss = (packet_loss / num_pings) * 100
min_rtt = min(rtts)
max_rtt = max(rtts)
avg_rtt = sum(rtts) / successful_pings

# Calculate Jitter
temp_sum = sum(abs(rtts[i] - rtts[i - 1]) for i in range(1, successful_pings))
jitter = temp_sum / (successful_pings - 1)

# Report statistics
print(f"Total packets sent: {num_pings}")
print(f"Packets acknowledged: {successful_pings}")
print(f"Packet loss: {percentage_loss:.0f}%")
print(f"Minimum RTT: {min_rtt:.0f} ms, Maximum RTT: {max_rtt:.0f} ms, Average RTT: {avg_rtt:.0f} ms")
# print(f"End time: {end_time}, Start time: {start_time}")
print(f"Total transmission time: {(total_time * 1000):.0f} ms") # time.time() is in seconds
print(f"Jitter: {jitter:.0f} ms")

clientSocket.close()
