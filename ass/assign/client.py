import threading
import time
import socket
import sys

def send_heartbeat(client_socket, username):
    '''
    send hearbeat to server at interval of 2 seconds
    to be used as a thread
    '''
    heartbeat_code = "HBT"
    heartbeat_msg = f"{heartbeat_code} {username}"
    while not stop_heartbeat:
        client_socket.sendto(heartbeat_msg.encode(), server_address)
        time.sleep(2)

def send_and_recieve_lap_request():
    lap_code = "LAP"
    lap_msg = f"{lap_code} {username}"
    print("sending lap request...")
    client_socket.sendto(lap_msg.encode(), server_address)
    server_response, _ = client_socket.recvfrom(1024)
    print("received a lap response")
    server_response = server_response.decode().split(' ')
    number_of_active_peers = int(server_response[1])
    if number_of_active_peers == 0:
        print("No active peers")
        return
    else:
        print(f"{number_of_active_peers} active peer")
    active_peers = server_response[2:]
    for peer in active_peers:
        print(peer)


# create socket
server_port = int(sys.argv[1])
server_IP = '127.0.0.1'
server_address = (server_IP, server_port)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# prompt for authentication
while True:
    auth_code = "AUTH"
    username = input("Enter username: ")
    password = input("Enter password: ")
    client_request = f"{auth_code} {username} {password}"

    client_socket.sendto(client_request.encode(), server_address)
    server_response, _ = client_socket.recvfrom(1024)
    
    server_response = server_response.decode().split(' ')
    respose_type = server_response[0]
    respose_note = server_response[1]

    if respose_type == "OK":
        print("Welcome to BitTrickle!")
        break
    else:
        print("Authentication failed. Please try again.")

# start heartbeat thread
HB_thread = threading.Thread(target=send_heartbeat, args=(client_socket, username))
stop_heartbeat = False
print("Starting heartbeat...")
HB_thread.start()

# prompt for user cmd
print("Available commands are: get, lap, lpf, pub, sch, unp, xit")
while True:
    command = input("> ").strip()

    if command.startswith("get "):
        filename = command.split(" ")[1]
        print(f"Attempting to get file '{filename}' from active peers...")
        continue
    elif command == "lap":
        print("Listing all active peers...")
        send_and_recieve_lap_request()
        continue
    elif command == "lpf":
        print("Listing all published files by this user...")
        continue
    elif command.startswith("pub "):
        filename = command.split(" ")[1]
        print(f"Publishing file '{filename}'...")
        continue
    elif command.startswith("sch "):
        substring = command.split(" ")[1]
        print(f"Searching for files containing '{substring}'...")
        continue
    elif command.startswith("unp "):
        filename = command.split(" ")[1]
        print(f"Unpublishing file '{filename}'...")
        continue
    elif command == "xit":
        print("Exiting BitTrickle...")
        break
    else:
        print("Unknown command. Please try again.")

# stop heartbeat thread and close UDP cocket
print("Stoping heartbeat...")
stop_heartbeat = True
HB_thread.join()
print("Closing socket...")
client_socket.close()


    

    

    



