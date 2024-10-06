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
    if username not in heartbeats_record:
        return False
    
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

def receive_request(request_type):
    client_port = client_address[1]
    username = client_request[1]
    display_msg_recieved(client_port, request_type, username)

def send_response(response_type, response_content):
    response = f"{response_type} {response_content}"
    server_socket.sendto(response.encode(), client_address)
    display_msg_sent(client_port, response_type, username)

def handle_AUTH():
    '''
    respond to client with "ERR" if username is already active, or credentials not match
    respond to client wtih "OK" if if successfuly added client to active_clients set
    '''
    receive_request("AUTH")
    password = client_request[2]

    response_type = "ERR"
    if not check_active(username) and check_credentials(username, password):
        response_type = "OK"
        active_clients.add(username)
        heartbeats_record[username] = time.time() # auth treated as a heartbeat

    response_content = ''
    send_response(response_type, response_content)

def handle_HBT():
    receive_request("HBT")
    heartbeats_record[username] = time.time()

    welcoming_port_number = client_request[2]
    contact_book[username] = welcoming_port_number
    # print(contact_book)

def handle_LAP():
    receive_request("LAP")

    for username in active_clients:
        check_active(username)
        if username not in active_clients:
            break

    response_type = "OK"
    response_content = f"{len(active_clients)} " + " ".join(str(c) for c in active_clients)
    send_response(response_type, response_content)

def handle_LPF():
    receive_request("LPF")
    
    files_that_I_publish = file_publishing_users[username]
    
    response_type = "OK"
    response_content = f"{len(files_that_I_publish)} " + " ".join(str(f) for f in files_that_I_publish)
    send_response(response_type, response_content)

def handle_PUB():
    receive_request("PUB")
    filename = client_request[2]
    
    if filename not in published_files:
        published_files[filename] = set()

    published_files[filename].add(username)
    file_publishing_users[username].add(filename)

    response_type = "OK"
    response_content = ''
    send_response(response_type, response_content)

def handle_UNP():
    receive_request("UNP")
    filename = client_request[2]

    response_type = "ERR"
    if filename in file_publishing_users[username]:
        file_publishing_users[username].remove(filename)
        published_files[filename].remove(username)
        response_type = "OK"

    response_content = ''
    send_response(response_type, response_content)

def handle_SCH():
    receive_request("SCH")
    substring = client_request[2]
    list_of_files_found = str()
    number_of_files_found = 0
    response_type = 'ERR'
    # print(substring)

    for user in active_clients:
        if user == username:
            continue
        for filename in file_publishing_users[user]:
            if substring in filename:
                list_of_files_found += ' '
                list_of_files_found += filename
                number_of_files_found += 1
                response_type = 'OK'
    
    response_content = f'{number_of_files_found}{list_of_files_found}'
    send_response(response_type, response_content)

server_port = int(sys.argv[1])
server_IP = '127.0.0.1'
server_address = (server_IP, server_port)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(server_address)

credentials = load_credentials('credentials.txt') # credentials dict for easier authentication
active_clients = set() # a set for unique usernames
heartbeats_record = {username: 0 for username in credentials}  # last heartbeat time for each user, initialised to be 0
published_files = {} # <filename: {set of clients with this file avaliable}>
file_publishing_users = {username: set() for username in credentials} # <username: {set of files published by this user}>
contact_book = {} # <username(could be offline): (last known) welcoming port number>

print("Server is now online")
while True:
    client_request, client_address = server_socket.recvfrom(1024)
    client_request = client_request.decode().split(' ')
    client_port = client_address[1]
    username = client_request[1]
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
        case "PUB":
            handle_PUB()
        case "UNP":
            handle_UNP()
        case "SCH":
            handle_SCH()

