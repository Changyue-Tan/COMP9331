// Sample network sockets code - UDP Server.
// Written for COMP3331 by Andrew Bennett, October 2019.
// ============================================================
// Modified by Wei Song (Tutor for COMP3331/9331), October 2021
// Modifications:  
// - UDP --> TCP
// - multi_treading


#include <arpa/inet.h>
#include <assert.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <unistd.h>

/*

A good reference for C sockets programming (esp. structs and syscalls):
https://beej.us/guide/bgnet/html/multi/index.html

And for information on C Threads:
https://www.gnu.org/software/libc/manual/html_node/ISO-C-Threads.html

One of the main structs used in this program is the "sockaddr_in" struct.
See: https://beej.us/guide/bgnet/html/multi/ipstructsdata.html#structs

struct sockaddr_in {
    short int          sin_family;  // Address family, AF_INET
    unsigned short int sin_port;    // Port number
    struct in_addr     sin_addr;    // Internet address
    unsigned char      sin_zero[8]; // Same size as struct sockaddr
};

*/


// Server host and port number are defined here for simple usage, but for some
// lab/assignment requires, they may need to be passed from command line parameter
// which should be obtained from the second parameter *argv[] of the main() function
#define SERVER_IP "127.0.0.1"
#define SERVER_PORT 12000

// Buffer length for messages exchanged between client and server
// 1024 is a normal case, it can also be specified as 2048 or others according to requirements
#define BUF_LEN 1024


// Handlers for the client thread
void* client_thread_handler(void *info);


int main(int argc, char *argv[]) {

    // Create the server's socket.
    //
    // The first parameter indicates the address family; in particular,
    // `AF_INET` indicates that the underlying network is using IPv4.
    //
    // The second parameter indicates that the socket is of type
    // SOCK_DGRAM, which means it is a UDP socket (rather than a TCP
    // socket, where we use SOCK_STREAM).
    int socket_desc, client_sock, client_size;
    struct sockaddr_in server_addr, client_addr;
    char server_message[BUF_LEN], client_message[BUF_LEN];
    
    // Clean buffers
    memset(server_message, '\0', sizeof(server_message));
    memset(client_message, '\0', sizeof(client_message));
    
    // Create server socket
    socket_desc = socket(AF_INET, SOCK_STREAM, 0);
    
    if(socket_desc < 0){
        printf("===== Error while creating socket =====\n");
        return -1;
    }
    printf("===== Socket created successfully =====\n");
    
    // Set server port and IP:
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(SERVER_PORT);
    server_addr.sin_addr.s_addr = inet_addr(SERVER_IP);
    
    // Bind to the set port and IP:
    if(bind(socket_desc, (struct sockaddr*)&server_addr, sizeof(server_addr))<0){
        printf("===== Couldn't bind to the port =====\n");
        return -1;
    }
    printf("===== Done with binding =====\n");
    
    // Listen for clients:
    if(listen(socket_desc, 5) < 0){
        printf("Error while listening\n");
        return -1;
    }
    printf("\nServer is running and listening for incoming connections.....\n");

    pthread_t client_thread;

    while (true) {
        // Accept an incoming connection:
        struct sockaddr_in client_addr;
        client_size = sizeof(client_addr);
        client_sock = accept(socket_desc, (struct sockaddr*)&client_addr, &client_size);
        
        if (client_sock < 0){
            printf("===== Can't accept =====\n");
            return -1;
        }

        printf("===== Client connected at IP: %s and port: %i =====\n", inet_ntoa(client_addr.sin_addr), ntohs(client_addr.sin_port));

        // create separate thread for each client
        pthread_create(&client_thread, NULL, client_thread_handler, &client_sock);
    }

    return 0;
}


void* client_thread_handler(void* p_client_sock) {
    int cs = *(int*)p_client_sock;

    // Receive client's message:
    char server_message[BUF_LEN], client_message[BUF_LEN];
    int clientAlive = 1;

    while (clientAlive) {
        // Clean buffers:
        memset(server_message, '\0', sizeof(server_message));
        memset(client_message, '\0', sizeof(client_message));

        int ret = recv(cs, client_message, sizeof(client_message), 0);
        if (ret == 0) {
            clientAlive = 0;
            printf("===== Client disconnected, its socket descriptor is %d ...\n =====", cs);
            break;
        }

        if (ret < 0){
            printf("===== Couldn't receive =====\n");
        }

        printf("[recv] Msg from client: %s\n", client_message);
        
        // Respond to client:
        strcpy(server_message, "This is the server's message");
        
        if (send(cs, server_message, strlen(server_message), 0) < 0){
            printf("===== Can't send =====\n");
            return NULL;
        }
        printf("[send] This is the server's message\n");
    }

    return NULL;
}


// Wrapper function for fgets, similar to Python's built-in 'input'
// function.
void get_input (char *buf, char *msg) {
    printf("%s", msg);
    fgets(buf, BUF_LEN, stdin);
    buf[strcspn(buf, "\n")] = '\0'; // Remove the newline
}