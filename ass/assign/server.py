import socket
import threading
import sys
import datetime

class BitTrickleClient:
    def __init__(self, username, address):
        self.username = username
        self.address = address  # (IP, port) tuple
    
    def __str__(self):
        return f"Client(username={self.username}, address={self.address})"

class BitTrickleServer:
    def __init__(self, port, credentials_dict):
        self.port = port
        self.credentials = credentials_dict
        self.online_clients = set()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind(('127.0.0.1', port))

    def authenticate(self, username, password):
        if username in self.credentials and self.credentials[username] == password:
            return True
        else:
            return False

    def handle_payload(self, payload, client_address):
        
        message = payload.decode().split(' ')
        code = message[0]

        if code == 'AUTH':
            username = message[1]
            password = message[2]
            print(f"Received {code} from {username}")
            self.authenticate(username, password)
        else:
            pass

 

        if self.authenticate(username, password):
            client = BitTrickleClient(username, client_address)
            self.online_clients.add(client) 
            response = "OK"
        else:
            response = "ERR"
        
        current_time = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        client_port = client_address[1]
        self.server_socket.sendto(response.encode(), client_address)
        print(f"{current_time}: {client_port}: Sent {response} to {username}")




def load_credentials(credentials_file):
    credentials = {}
    with open(credentials_file, 'r') as f:
        for line in f:
            username, password = line.strip().split(' ')
            credentials[username] = password
    return credentials 


if __name__ == "__main__":

    creddentials_dict = load_credentials('credentials.txt')
    server = BitTrickleServer(int(sys.argv[1]), creddentials_dict) 

    print(f"Server is listening on port {server.port} for authetication requests...")
    
    while True:
        payload, client_address = server.server_socket.recvfrom(1024)
        client_thread = threading.Thread(target=server.handle_payload, args=(payload, client_address))
        client_thread.start()
