import socket
import threading
import sys
import datetime

class BitTrickleClient:
    def __init__(self, username, client_address):
        self.username = username
        self.address = client_address  # (IP, port) tuple
        self.availability = False
    
    def __str__(self):
        return f"Client(username={self.username}, address={self.address})"

class BitTrickleServer:
    def __init__(self, server_port, credentials_file):

        self.credentials = {}
        with open(credentials_file, 'r') as f:
            for line in f:
                username, password = line.split(' ')
                self.credentials[username] = password
            
        self.active_clients = {}
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind(('127.0.0.1', server_port))

    def authenticate(self, username, password):
        if username in self.credentials and self.credentials[username] == password:
            return True
        else:
            return False

    def handle_client(self, payload, client_address):
        
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
            self.active_clients[client_address] = client
            response = "OK"
        else:
            response = "ERR"
        
        current_time = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        client_port = client_address[1]
        self.server_socket.sendto(response.encode(), client_address)
        print(f"{current_time}: {client_port}: Sent {response} to {username}")







if __name__ == "__main__":

    credentials_file = 'credentials.txt'
    server_port = int(sys.argv[1])
    server = BitTrickleServer(server_port, credentials_file) 

    print(f"Server is listening for authetication requests...")
    
    while True:
        payload, client_address = server.server_socket.recvfrom(1024)
        client_thread = threading.Thread(target=server.handle_client, args=(payload, client_address))
        client_thread.start()
