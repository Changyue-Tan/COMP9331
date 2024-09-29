import threading
import time
import socket
import sys


if __name__ == "__main__":
    
    server_port = int(sys.argv[1])
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    username = input("Enter username: ")
    password = input("Enter password: ")
    message = f"{username} {password}"
    client_socket.sendto(message.encode(), ('127.0.0.1', server_port))
    response, server_add= client_socket.recvfrom(1024)
    print(f"Server response from {server_add}: {response.decode()}")


