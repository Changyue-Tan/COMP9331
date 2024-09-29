import threading
import time
import socket
import sys


def authenticate(client_socket):
    while True:
        username = input("Enter username: ")
        password = input("Enter password: ")
        code = "AUTH"
        payload = f"{code} {username} {password}"

        client_socket.sendto(payload.encode(), ('127.0.0.1', server_port))
        response, _ = client_socket.recvfrom(1024)

        if response.decode() == "OK":
            print("Welcome to BitTrickle!")
            print("Available commands are: get, lap, lpf, pub, sch, unp, xit")
            return username, client_socket
        else:
            print("Authentication failed. Please try again.")

def send_heartbeat():
    print("Sending heartbeat to server...")
    time.sleep(2)

def prompt_for_commands():
    while True:
        command = input("> ").strip()

        if command.startswith("get "):
            filename = command.split(" ")[1]
            print(f"Attempting to get file '{filename}' from active peers...")

        elif command == "lap":
            print("Listing all active peers...")

        elif command == "lpf":
            print("Listing all published files by this user...")

        elif command.startswith("pub "):
            filename = command.split(" ")[1]
            print(f"Publishing file '{filename}'...")

        elif command.startswith("sch "):
            substring = command.split(" ")[1]
            print(f"Searching for files containing '{substring}'...")

        elif command.startswith("unp "):
            filename = command.split(" ")[1]
            print(f"Unpublishing file '{filename}'...")

        elif command == "xit":
            print("Exiting BitTrickle...")
            break

        else:
            print("Unknown command. Please try again.")

if __name__ == "__main__":
    
    server_port = int(sys.argv[1])
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    username = authenticate(client_socket)
    send_heartbeat()
    HB_thread = threading.Thread(target=server.handle_client, args=(username))
    prompt_for_commands()

    

    

    



