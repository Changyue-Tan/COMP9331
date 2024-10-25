import threading
import time
import socket
import sys

stop_welcome = False
stop_heartbeat = False
welcoming_port_ready = threading.Event()
welcoming_port_number = None
download_threads = []  
upload_threads = []  

def downloading_sequence(peer_port_number, download_filename, peername):
    download_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peer_address = ('localhost', int(peer_port_number))
    
    print(f"Connecting to {peername} at {peer_address}")
    download_socket.connect(peer_address)
    print("Connection established!")
    print(f"Telling peer which file is wanted:'{filename}'...")
    download_socket.sendall(download_filename.encode())

    with open(f"{download_filename}", "wb") as f:
        print(f"Downloading '{download_filename}' from {peername}...")
        while True:
            data = download_socket.recv(1024)  # Receive in 1KB chunks
            if not data:
                break
            f.write(data)
    
    print(f"'{download_filename}' downloaded successfully!")
    print(f"Closing P2P connection with {peername}...")
    download_socket.close()
    
def uploading_sequence(upload_socket, peer_address):
    
    print("Recieving which file this peer wants...")
    requested_filename = upload_socket.recv(1024).decode()
    print(f"Peer wants {requested_filename}")
    print("Sending data...")
    with open(requested_filename, "rb") as f:
            while True:
                data = f.read(1024)  # Send the file in chunks
                if not data:
                    break
                upload_socket.send(data)

    print(f"'{requested_filename}' uploaded successfully!")
    print(f"Closing P2P connection with {peer_address}...")
    upload_socket.close()

def create_welcoming_socket():
    welcoming_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    welcoming_socket.bind(('localhost', 0)) # 0 means the OS can choose any available port
    global welcoming_port_number 
    welcoming_port_number = welcoming_socket.getsockname()[1]  

    welcoming_port_ready.set()

    # print(f'Listening for P2P TCP connection request from port: {welcoming_port_number}')
    welcoming_socket.listen()
    while not stop_welcome:
        upload_socket, client_addr = welcoming_socket.accept()
        print(f"New P2P connection from {client_addr}") # We do not know the peer's name here
        
        if not stop_welcome:
            print(f"Starting file uploading sequence to {client_addr}...")
            UPLOAD_thread = threading.Thread(target=uploading_sequence, args=(upload_socket, client_addr))
            UPLOAD_thread.start()
            upload_threads.append(UPLOAD_thread)
        else:
            print("STOP_WELCOME_FLAG is set, this is a psuedo request")
            print("Welcoming_socket stops accepting connection")

    print("Closing welcoming socket...")
    welcoming_socket.close()

def send_heartbeat(client_socket, username):
    '''
    send hearbeat to server at interval of 2 seconds
    to be used as a thread
    '''
    heartbeat_code = "HBT"

    welcoming_port_ready.wait() # wait for welcoming socket to be created in another thread
    # print(welcoming_port_number)
    # welcoming port number will be sent as well
    heartbeat_msg = f"{heartbeat_code} {username} {welcoming_port_number}"
    while not stop_heartbeat:
        client_socket.sendto(heartbeat_msg.encode(), server_address)
        time.sleep(2)

def send_and_recieve(request_msg):
    client_socket.sendto(request_msg.encode(), server_address)
    server_response, _ = client_socket.recvfrom(1024)
    server_response = server_response.decode().split(' ')
    return server_response

def handle_get_request(filename):
    request_code = "GET"
    request_msg = f"{request_code} {username} {filename}"
    server_response = send_and_recieve(request_msg)

    if server_response[0] == "OK":
        arbitary_available_user = server_response[1]
        address_of_available_user = server_response[2] # address wil only be port number
        print(f"User {arbitary_available_user} has {filename}") 
        print(f"{arbitary_available_user} is currently online with welcoming port: {address_of_available_user}")    
        print(f"Starting file downloading sequence from {arbitary_available_user}...")
        
        DOWNLOAD_thread = threading.Thread(target=downloading_sequence, args=(address_of_available_user, filename, arbitary_available_user))
        DOWNLOAD_thread.start()
        download_threads.append(DOWNLOAD_thread)

    else:
        print("No file found")

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

def handle_sch_request(substring):
    request_code = "SCH"
    request_msg = f"{request_code} {username} {substring}"
    server_response = send_and_recieve(request_msg)
    # print(server_response)

    if server_response[0] == "OK":
        number_files_found = server_response[1]
        if number_files_found == '0':
            print("File not found")
            return
        elif number_files_found == '1':
            print("1 file found:")
        else:
            print(f"{number_files_found} files found:")
        
        for filename in server_response[2:]:
            print(filename)


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
        print("Starting client booting sequence...")
        break
    else:
        print("Authentication failed. Please try again.")

# start TCP welcoming thread
WELCOME_thread = threading.Thread(target=create_welcoming_socket)
# start heartbeat thread
HB_thread = threading.Thread(target=send_heartbeat, args=(client_socket, username))



print("Starting welcoming thread...")
WELCOME_thread.start()

# welcoming port number will be sent via heart beat

print("Starting heartbeat thread...")
HB_thread.start()

print("Client is now online")

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
                # print(f"Attempting to get file '{filename}' from active peers...")
                handle_get_request(filename)
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
                print("Missing substring")
            else: 
                substring = request_content
                # print(f"Searching for files containing '{substring}'...")
                handle_sch_request(substring)
        case "unp":
            if request_content == None:
                print("Missing filename")
            else: 
                filename = request_content
                handle_unp_request(filename)
        case "xit":
            print("Starting client shutdown sequence...")
            print("A psuedo request will be sent to welcoming socket")
            break
        case _:
            print("Unknown command. Please try again.")


stop_welcome = True

# Open a connection to the welcoming socket to unblock the accept() call
temp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
temp_socket.connect(('localhost', welcoming_port_number))
temp_socket.close()

print("Waiting for WELCOME_thread to finish...")
WELCOME_thread.join()
print("WELCOME_thread finished")

stop_heartbeat = True
print("Waiting for HB_thread to finish...")
HB_thread.join()
print("HB_thread finished")

print("Closing UDP socket with server...")
client_socket.close()

print("Waiting for P2P uploads to finish...")
for thread in upload_threads:
    thread.join() 
    # print("upload finished")

print("Waiting for P2P downloads to finish...")
for thread in download_threads:
    thread.join()
    # print("download finished")

print("Client is now offline")


    

    

    



