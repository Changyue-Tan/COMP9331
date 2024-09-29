import threading
import time
import socket
import sys


if __name__ == "__main__":
    
    server_port = int(sys.argv[1])
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while 1:
        username = input("Enter username: ")
        password = input("Enter password: ")
        code = "AUTH"
        payload = f"{code} {username} {password}"

        client_socket.sendto(payload.encode(), ('127.0.0.1', server_port))
        response, _ = client_socket.recvfrom(1024)

        if response.decode() == "OK":
            print("Welcome to BitTrickle!")
            sys.exit()
        else:
            print("Authentication failed. Please try again.")


