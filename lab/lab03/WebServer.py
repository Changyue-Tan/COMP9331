import socket
import os
import sys

HOST = '127.0.0.1'  
PORT =  int(sys.argv[1])     

def send_response(code, content=b''):
    match code:
        case 200:
            server_log = 'Sending OK to client...'
            response_header = 'HTTP/1.1 200 OK \r\n'
            if content == b'':
                content = b'<h1>200 OK</h1>'
        case 204:
            server_log = 'Sending 204 to client...'
            response_header = 'HTTP/1.1 204 No Content\r\n'
            content = b'<h1>204 No Content</h1>'
        case 400:
            server_log = "Sending 400 to client..."
            response_header = 'HTTP/1.1 400 Bad Request\r\n'
            content = b'<h1>400 Bad Request</h1>'
        case 404:
            server_log = "Sending 404 to client..."
            response_header = 'HTTP/1.1 404 Not Found\r\n'
            content = b'<h1>404 Not Found</h1>'
        case 405:
            server_log = "Sending 405 to client..."
            response_header = 'HTTP/1.1 405 Method Not Allowed\r\n'
            content = b'<h1>405 Method Not Allowed</h1>'

    print(server_log)
    
    response_header += 'Connection: keep-alive\r\n'
    response_header += f'Content-Length: {len(content)}\r\n'
    response_header += '\r\n'

    connection_socket.sendall(response_header.encode() + content)

def handle_connection(connection_socket):
    empty_request_counter = 0 # TCP tear down requires 4-way handshake

    while True:
        print(f"\nStarts listening for new request sent to this connection socket...")
        request = connection_socket.recv(1024).decode()

        if not request:
            empty_request_counter += 1
            print(f'Empty request. TCP connection tear down: #{empty_request_counter}')
            # FIN from Client + ACK from Client = 2
            if empty_request_counter == 2: 
                break
            send_response(200)

        else:
            lines = request.splitlines()
            request_line = lines[0]
            method, path, version = request_line.split()

            if method == 'GET' and version == 'HTTP/1.1':
                filename = path.lstrip('/')

                if filename == "favicon.ico":
                    print("Request for \"favicon.ico\"")
                    send_response(204)

                elif os.path.isfile(filename):
                    print(f"Request for {filename}")
                    with open(filename, 'rb') as f: # read as binary
                        content = f.read()  
                    send_response(200, content)
                    
                else:
                    print("The server does not have the requested file")
                    send_response(404)

            else:
                print("The server is not configuted to handle this request")
                send_response(405)

            print("A request have been handled and response sent")
    
welcoming_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
welcoming_socket.bind((HOST, PORT))
welcoming_socket.listen(1)  # specifies the backlog (number of pending connections that can be queued).
welcoming_socket.settimeout(20) # 20 seconds timeout if no connection request

while True:
    print(f'\nListening on port: {PORT} for TCP connection request...')
    try:
        connection_socket, client_addr = welcoming_socket.accept()
        print(f'TCP connection request from: <IP: {client_addr[0]}, Port: {client_addr[1]}>')
        print('A socket has been created for this client')
        with connection_socket:
            handle_connection(connection_socket)
            print("Client closed the TCP connection")

    except socket.timeout:
        print("Timed out while waiting for connection request")
        break

    except Exception as e:
        print(f"An unknown error occurred: {e}")

print("Closing welcoming socket...")
welcoming_socket.close()    
print("Server shutting down...")

