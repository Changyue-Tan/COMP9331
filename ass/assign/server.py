import socket
import sys
import datetime
import time

def load_credentials(credentials_file):
    credentials = {}
    with open(credentials_file, 'r') as f:
        for line in f:
            username, password = line.strip().split(' ')
            credentials[username] = password
    return credentials

def display_msg_recieved(client_port, request_type, username):
    current_time = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
    msg = f"Received {request_type} from {username}"
    print(f"{current_time}: {client_port}: {msg}")

def display_msg_sent(client_port, response_type, username):
    current_time = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
    msg = f"Sent {response_type} to {username}"
    print(f"{current_time}: {client_port}: {msg}")

def check_active(username):
    last_heartbeat_time = heartbeats_record[username]
    current_time = time.time()
    if username in active_clients:
        if (current_time - last_heartbeat_time) > 3:
            active_clients.remove(username)
            return False
        else:
            return True
    else:
        False

def check_credentials(username, password):
    return username in credentials and credentials[username] == password

def handle_AUTH():
    '''
    respond to client with "ERR" if username is already active, or credentials not match
    respond to client wtih "OK" if if successfuly added client to active_clients set
    '''
    request_type = "AUTH"
    client_port = client_address[1]
    username = client_request[1]
    password = client_request[2]
    display_msg_recieved(client_port, request_type, username)

    response_type = "ERR"
    response_note = "Authentication failed"

    if not check_active(username) and check_credentials(username, password):
        response_type = "OK"
        response_note = "Authentication successful"
        active_clients.add(username)
        heartbeats_record[username] = time.time() # auth treated as a heartbeat

    response = f"{response_type} {response_note}"
    display_msg_sent(client_port, response_type, username)
    server_socket.sendto(response.encode(), client_address)

def handle_HBT():
    request_type = "HBT"
    client_port = client_address[1]
    username = client_request[1]
    display_msg_recieved(client_port, request_type, username)
    heartbeats_record[username] = time.time()

def handle_LAP():
    pass

def handle_LPF():
    pass


server_port = int(sys.argv[1])
server_IP = '127.0.0.1'
server_address = (server_IP, server_port)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(server_address)

credentials = load_credentials('credentials.txt') # credentials dict for easier authentication
active_clients = set() # a set for unique usernames
heartbeats_record = {username: 0 for username in credentials}  # last heartbeat time for each user, initialised to be 0

print(f"Server starts listening on {server_address} ...")
while True:
    client_request, client_address = server_socket.recvfrom(1024)
    client_request = client_request.decode().split(' ')
    request_type = client_request[0]
    match request_type:
        case "AUTH":
            handle_AUTH()
        case "HBT":
            handle_HBT()
        case "LAP":
            handle_LAP()
        case "LPF":
            handle_LPF()

