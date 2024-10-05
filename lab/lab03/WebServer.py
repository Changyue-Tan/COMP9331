import socket
import os
import sys

HOST = '127.0.0.1'  
PORT =  int(sys.argv[1])     

MIME_TYPES = {
    'html': 'text/html',
    'htm': 'text/html',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
    'gif': 'image/gif',
    'ico': 'image/x-icon',
    'css': 'text/css',
    'js': 'application/javascript',
    'txt': 'text/plain',
    'json': 'application/json',
}

def get_content_type(filename):
    _, ext = os.path.splitext(filename)
    ext = ext[1:]
    return MIME_TYPES.get(ext, 'application/octet-stream') 

def handle_connection(connection_socket):
    keep_alive = True # will be false if the client wishes the connection closed
    # request_counter = 0 # each connection will only handle max 100 request
    # empty_request_counter = 0

    while keep_alive: # and request_counter <= 100:
        
        # request_counter += 1
        print(f"Starts listening for new request sent to this connection socket...")

        request = connection_socket.recv(1024).decode()

        # try:
        #     request = connection_socket.recv(1024).decode()
        # except socket.timeout:
        #     print("Timed out while waiting for client request.")
        #     print("Sending closing notification to client")
        #     response_header = 'HTTP/1.1 200 OK\r\n'
        #     # response_header += 'Content-Type: text/html\r\n'
        #     response_body = '<h1>Connection will be closed</h1>'
        #     response_header += f'Content-Length: {len(response_body)}\r\n'
        #     response_header += 'Connection: close\r\n\r\n'  
        #     connection_socket.sendall(response_header.encode() + response_body.encode())
        #     break
    
        if not request:

            # empty_request_counter += 1
            # if empty_request_counter == 2:
            #     keep_alive = False
            #     continue


            print('EMPTY REQUEST')
            print('Sending OK to client...')
            response_header = 'HTTP/1.1 200 OK \r\n'
            # response_header += 'Keep-Alive: timeout=10\r\n'
            response_header += 'Connection: keep-alive\r\n'
            response_header += 'Content-Type: text/html\r\n'
            response_body = '<h1>200 OK</h1>'
            response_header += f'Content-Length: {len(response_body)}\r\n' 
            response_header += '\r\n'
            try:
                connection_socket.sendall(response_header.encode() + response_body.encode())
            except BrokenPipeError:
                print("Broken pipe error: The client has closed the connection.")
                keep_alive = False

        else:
            lines = request.splitlines()
            if 'Connection: close' in lines:
                print("Client wishes the connection closed")
                keep_alive = False
            
            print("New request recieved! Printing request for examination...")
            print("-------------Start of request-------------")
            print(request) 
            print("-------------End of request---------------")
            print("Printing finished! Parsing & handling request...")

            if "Connection: close" in lines:
                keep_alive = False

            request_line = lines[0]
            method, path, version = request_line.split()

            if method == 'GET' and version == 'HTTP/1.1':
                filename = path.lstrip('/')

                if filename == "favicon.ico":
                    print("This is a request for the icon to be displayed in browser's address bar\n"
                          "Sending 204 to client...")
                    response_header = 'HTTP/1.1 204 No Content\r\n'
                    response_header += 'Connection: keep-alive\r\n'
                    response_header += '\r\n'
                    connection_socket.sendall(response_header.encode())

                elif os.path.isfile(filename):
                    print("The server has the requested file!\n" 
                          "Sending it to client...")
                    with open(filename, 'rb') as f: # 'rb' read file as binary 
                        content = f.read()  
                    
                    content_type = get_content_type(filename)

                    response_header = 'HTTP/1.1 200 OK\r\n'
                    # response_header += 'Keep-Alive: timeout=10\r\n'
                    response_header += 'Connection: keep-alive\r\n'
                    response_header += f'Content-Type: {content_type}\r\n'
                    response_header += f'Content-Length: {len(content)}\r\n'  
                    response_header += '\r\n'
                    connection_socket.sendall(response_header.encode() + content)
                else:
                    print("The server does not have the requested file!\n"
                          "Sending 404 to client...")
                    response_header = 'HTTP/1.1 404 Not Found\r\n'
                    # response_header += 'Keep-Alive: timeout=10\r\n'
                    response_header += 'Connection: keep-alive\r\n'  
                    response_body = '<h1>404 Not Found</h1>'
                    response_header += f'Content-Length: {len(response_body)}\r\n' 
                    response_header += '\r\n'
                    connection_socket.sendall(response_header.encode() + response_body.encode())
            else:
                print("The server is not configuted to handle this request!\n"
                      "Sending 400 to client...")
                response_header = 'HTTP/1.1 400 Bad Request\r\n'
                # response_header += 'Keep-Alive: timeout=10\r\n'
                response_header += 'Connection: keep-alive\r\n'
                response_body = '<h1>400 Bad Request</h1>'
                response_header += f'Content-Length: {len(response_body)}\r\n'
                response_header += '\r\n'   
                connection_socket.sendall(response_header.encode() + response_body.encode())
        
            print("A request have been successfully handled!")
    
    print("No more requests anticipatd from this connection, closing connection socket...")
    connection_socket.close()


welcoming_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
welcoming_socket.bind((HOST, PORT))

welcoming_socket.listen(1)  # specifies the backlog (number of pending connections that can be queued).
welcoming_socket.settimeout(20) # set a timeout for welcoming socket

while True:
    print(f'\nStarts listening on port: {PORT} for new connection request...')

    try:
        connection_socket, client_addr = welcoming_socket.accept()
    except socket.timeout:
        print("Timed out while waiting for connection request\n"
              "Closing welcoming socket...")
        welcoming_socket.close()
        break

    # connection_socket.settimeout(20) # set a timeout for connection socket

    print(f'New connection request from: <IP: {client_addr[0]}, Port: {client_addr[1]}>')
    print('A new connection socket has been created for this client')
    print('Handling the connection...')
    handle_connection(connection_socket)

