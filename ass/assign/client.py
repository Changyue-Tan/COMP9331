import threading
import time
import socket
import sys

def send_heartbeat(client_socket, username):
    heartbeat_code = "HBT"
    heartbear_msg = f"{heartbeat_code} {username}"
    while not stop_heartbeat:
        client_socket.sendto(heartbear_msg.encode(), server_address)
        time.sleep(2)

server_port = int(sys.argv[1])
server_IP = '127.0.0.1'
server_address = (server_IP, server_port)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
while True:
    auth_code = "AUTH"
    username = input("Enter username: ")
    password = input("Enter password: ")
    client_request = f"{auth_code} {username} {password}"

    client_socket.sendto(client_request.encode(), server_address)
    server_response, _ = client_socket.recvfrom(1024)
    
    message = server_response.decode().split(' ')
    respose_type = message[0]
    respose_note = message[1]

    if respose_type == "OK":
        print("Welcome to BitTrickle!")
        break
    else:
        print("Authentication failed. Please try again.")


HB_thread = threading.Thread(target=send_heartbeat, args=(client_socket, username))
stop_heartbeat = False
print("Starting heartbeat...")
HB_thread.start()

print("Available commands are: get, lap, lpf, pub, sch, unp, xit")
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

print("Stoping heartbeat...")
stop_heartbeat = True
HB_thread.join()


    

    

    



