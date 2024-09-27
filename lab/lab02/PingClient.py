#coding: utf-8
from socket import *
import sys

# Get command-line arguments
args = sys.argv

host = args[1]
port = args[2]

# serverName = 'localhost'
serverName = host
serverPort = port

clientSocket = socket(AF_INET, SOCK_DGRAM)

message = input("Input some sentence:")

clientSocket.sendto(message.encode('utf-8'),(serverName, serverPort))
# Note the difference between UDP sendto() and TCP send() calls. In TCP we do not need to attach the destination address to the packet, while in UDP we explicilty specify the destination address + Port No for each message

modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
# Note the difference between UDP recvfrom() and TCP recv() calls.

print(modifiedMessage.decode('utf-8'))
# print the received message

clientSocket.close()
# Close the socket