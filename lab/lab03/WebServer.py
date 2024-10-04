import socket
import os

# Server configuration
HOST = '127.0.0.1'  # Localhost
PORT = 8080          # Port to listen on

def handle_request(client_socket):
    request = client_socket.recv(1024).decode()
    print(f"Received request:\n{request}")

    # Split request into lines
    lines = request.splitlines()
    if len(lines) > 0:
        # Get the first line (request line)
        request_line = lines[0]
        # Parse the request line
        method, path, _ = request_line.split()

        if method == 'GET':
            # Strip the leading '/' from the path
            filename = path.lstrip('/')

            # Check if file exists
            if os.path.isfile(filename):
                with open(filename, 'rb') as f:
                    content = f.read()
                # Create HTTP response header
                response_header = 'HTTP/1.1 200 OK\r\n'
                response_header += 'Content-Length: {}\r\n'.format(len(content))
                response_header += 'Connection: keep-alive\r\n\r\n'  # Persistent connection
                # Send the response
                client_socket.sendall(response_header.encode() + content)
            else:
                # File not found
                response_header = 'HTTP/1.1 404 Not Found\r\n'
                response_header += 'Connection: close\r\n\r\n'  # Close the connection for 404
                response_body = '<h1>404 Not Found</h1>'
                client_socket.sendall(response_header.encode() + response_body.encode())
        else:
            # Method not allowed
            response_header = 'HTTP/1.1 405 Method Not Allowed\r\n'
            response_header += 'Connection: close\r\n\r\n'
            client_socket.sendall(response_header.encode())
    client_socket.close()

def start_server():
    # Create a TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)  # Listen for incoming connections
    print(f'Server listening on {HOST}:{PORT}')

    while True:
        # Accept a connection from a client
        client_socket, addr = server_socket.accept()
        print(f'Connection from {addr}')
        
        # Handle the request
        handle_request(client_socket)

if __name__ == '__main__':
    start_server()
