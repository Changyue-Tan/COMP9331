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

def send_and_recieve(request_msg):
    client_socket.sendto(request_msg.encode(), server_address)
    server_response, _ = client_socket.recvfrom(1024)
    server_response = server_response.decode().split(' ')
    return server_response

def handle_lap_request():
    request_code = "LAP"
    request_msg = f"{request_code} {username}"
    server_response = send_and_recieve(request_msg)
    
    number_of_active_peers = int(server_response[1]) - 1 # exclude yourself
    active_peers = server_response[2:]
    if number_of_active_peers == 0: 
        print("No active peers")
        return
    elif number_of_active_peers == 1:
        print("1 active peer")
    else:
        print(f"{number_of_active_peers} active peers")
    
    for peer in active_peers:
        if peer != username:
            print(peer)

def handle_lpf_request():
    request_code = "LPF"
    request_msg = f"{request_code} {username}"
    server_response = send_and_recieve(request_msg)

    number_of_files_published = int(server_response[1])
    if number_of_files_published == 0:
        print("No files published")
        return
    elif number_of_files_published == 1:
        print("1 file published:")
    else:
        print(f"{number_of_files_published} files published:")

    files_published = server_response[2:]
    for file_name in files_published:
        print(file_name)

def handle_pub_request(filename):
    request_code = "PUB"
    request_msg = f"{request_code} {username} {filename}"
    server_response = send_and_recieve(request_msg)

    if server_response[0] == "OK":
        print("File published successfully")
    else:
        print("File publication failed")

def handle_unp_request(filename):
    request_code = "UNP"
    request_msg = f"{request_code} {username} {filename}"
    server_response = send_and_recieve(request_msg)

    if server_response[0] == "OK":
        print("File unpublished successfully")
    else:
        print("File unpublication failed")

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
    command = input("> ").strip().split(" ")
    request_type = command[0]
    request_content = None
    if len(command) > 1:
        request_content = command[1]
    
    match request_type:
        case "get":
            if request_content == None:
                print("Missing filename")
            else:
                filename = request_content
                print(f"Attempting to get file '{filename}' from active peers...")
        case "lap":
            handle_lap_request()
        case "lpf":
            handle_lpf_request()
        case "pub":
            if request_content == None:
                print("Missing filename")
            else:
                filename = request_content
                handle_pub_request(filename)
        case "sch":
            if request_content == None:
                print("Missing keyword")
            else: 
                keyword = request_content
                print(f"Searching for files containing '{keyword}'...")
        case "unp":
            if request_content == None:
                print("Missing filename")
            else: 
                filename = request_content
                handle_unp_request(filename)
        case "xit":
            print("Exiting BitTrickle...")
            break
        case "_":
            print("Unknown command. Please try again.")

# stop heartbeat thread and close UDP cocket
print("Stoping heartbeat...")
stop_heartbeat = True
HB_thread.join()
print("Closing socket...")
client_socket.close()


    

    

    



