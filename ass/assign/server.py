import socket
import threading
import sys

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

    def handle_client(self, data, client_address):
        try:
            username, password = data.decode().split(' ')
        except ValueError:
            self.server_socket.sendto("Invalid input format".encode(), client_address)
            return

        if self.authenticate(username, password):
            client = BitTrickleClient(username, client_address)
            self.online_clients.add(client) 
            response = "Authentication successful"
            print(f"Success. Client authenticated: {client}")
            print("current online clients:")
            print(self.online_clients)
        else:
            response = "Authentication failed"
            print(f"Failed. Sent failure notice to {client}")

        self.server_socket.sendto(response.encode(), client_address)



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
        data, client_address = server.server_socket.recvfrom(1024)
        client_thread = threading.Thread(target=server.handle_client, args=(data, client_address))
        client_thread.start()
