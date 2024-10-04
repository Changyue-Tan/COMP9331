import socket
import os
import sys

HOST = '127.0.0.1'  
PORT =  int(sys.argv[1])     

def handle_connection(connection_socket):
    keep_alive = True
    while keep_alive:
        print("Starts listening for new requests sent to this connection socket...")

        try:
            request = connection_socket.recv(1024).decode()
        except socket.timeout:
            print("Timed out while waiting for client request.")
            break

        lines = request.splitlines()
        if len(lines) == 0:
            print("Recieved an empty request\n"
                  "Telling the client that we wish the connection closed")
            response_header = 'HTTP/1.1 200 OK\r\n'
            response_header += 'Connection: close\r\n\r\n'
            connection_socket.sendall(response_header.encode())
            break

        else:
            print("New request recieved! Printing request for examination...")
            print("-------------Start of request-------------")
            print(request) 
            print("-------------End of request---------------")
            print("Printing finished! Parsing & handling request...")
            
            if 'Connection: close' in lines:
                keep_alive = False

            request_line = lines[0]
            method, path, version = request_line.split()

            if method == 'GET' and version == 'HTTP/1.1':
                filename = path.lstrip('/')

                if filename == "favicon.ico":
                    print("This is a request for the icon to be displayed in browser's address bar\n"
                          "Sending 204 to client...")
                    response_header = 'HTTP/1.1 204 No Content\r\n'
                    response_header += 'Connection: close\r\n\r\n'
                    response_body = '<h1>204 No Content</h1>'
                    connection_socket.sendall(response_header.encode() + response_body.encode())

                elif os.path.isfile(filename):
                    print("The server has the requested file!\n" 
                          "Sending it to client...")
                    with open(filename, 'rb') as f: # 'rb' read file as binary 
                        content = f.read()  
                    
                    response_header = 'HTTP/1.1 200 OK\r\n'
                    response_header += f'Content-Length: {len(content)}\r\n'
                    response_header += 'Connection: keep-alive\r\n\r\n'  
                    connection_socket.sendall(response_header.encode() + content)
                else:
                    print("The server does not have the requested file!\n"
                          "Sending 404 to client...")
                    response_header = 'HTTP/1.1 404 Not Found\r\n'
                    response_header += 'Connection: close\r\n\r\n' 
                    response_body = '<h1>404 Not Found</h1>'
                    connection_socket.sendall(response_header.encode() + response_body.encode())
            else:
                print("The server is not configuted to handle this request!\n"
                      "Sending 400 to client...")
                response_header = 'HTTP/1.1 400 Bad Request\r\n'
                response_header += 'Connection: close\r\n\r\n'
                connection_socket.sendall(response_header.encode())
        
            print("A request have been successfully handled!")
    
    print("No more requests anticipatd from this connection, closing connection socket...")
    connection_socket.close()


welcoming_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
welcoming_socket.bind((HOST, PORT))

welcoming_socket.listen(1)  # specifies the backlog (number of pending connections that can be queued).
welcoming_socket.settimeout(30) # set a timeout for welcoming socket

while True:
    print(f'\nStarts listening on port: {PORT} for new connection request...')

    try:
        connection_socket, client_addr = welcoming_socket.accept()
    except socket.timeout:
        print("Timed out while waiting for connection request\n"
              "Shutting down server...")
        welcoming_socket.close()
        break

    connection_socket.settimeout(30) # set a timeout for connection socket

    print(f'New connection request from: <IP: {client_addr[0]}, Port: {client_addr[1]}>')
    print('A new connection socket has been created for this client')
    print('Handling the connection...')
    handle_connection(connection_socket)

