#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>

#define MAX_BUFFER 1024
#define MAX_CLIENTS 100
#define MAX_FILES 100

// 数据结构声明
typedef struct {
    char username[MAX_BUFFER];
    char password[MAX_BUFFER];
} Credential;

typedef struct {
    char username[MAX_BUFFER];
    time_t last_heartbeat;
} ActiveClient;

typedef struct {
    char filename[MAX_BUFFER];
    char owner[MAX_BUFFER];
} PublishedFile;

// 全局变量
Credential credentials[MAX_CLIENTS];
ActiveClient active_clients[MAX_CLIENTS];
PublishedFile published_files[MAX_FILES];
int num_clients = 0;
int num_published_files = 0;

// 函数声明
void load_credentials(const char *credentials_file);
void handle_AUTH(int sockfd, struct sockaddr_in *client_addr, socklen_t client_len, const char *username, const char *password, int client_port);
void handle_HBT(const char *username);
void handle_LAP(int sockfd, struct sockaddr_in *client_addr, socklen_t client_len, int client_port);
void handle_LPF(int sockfd, struct sockaddr_in *client_addr, socklen_t client_len, const char *username, int client_port);
void handle_PUB(int sockfd, struct sockaddr_in *client_addr, socklen_t client_len, const char *username, const char *filename, int client_port);
void handle_UNP(int sockfd, struct sockaddr_in *client_addr, socklen_t client_len, const char *username, const char *filename, int client_port);
int check_credentials(const char *username, const char *password);
int check_active(const char *username);
void display_msg_received(int client_port, const char *request_type, const char *username);
void display_msg_sent(int client_port, const char *response_type, const char *username);
void send_response(int sockfd, struct sockaddr_in *client_addr, socklen_t client_len, const char *response_type, const char *response_content, int client_port, const char *username);

// 加载凭据
void load_credentials(const char *credentials_file) {
    FILE *file = fopen(credentials_file, "r");
    if (!file) {
        perror("Failed to open credentials file");
        exit(EXIT_FAILURE);
    }

    while (fscanf(file, "%s %s", credentials[num_clients].username, credentials[num_clients].password) != EOF) {
        num_clients++;
    }
    fclose(file);
}

// 检查凭据
int check_credentials(const char *username, const char *password) {
    for (int i = 0; i < num_clients; i++) {
        if (strcmp(credentials[i].username, username) == 0 && strcmp(credentials[i].password, password) == 0) {
            return 1;  // 匹配成功
        }
    }
    return 0;  // 匹配失败
}

// 检查是否活跃
int check_active(const char *username) {
    for (int i = 0; i < num_clients; i++) {
        if (strcmp(active_clients[i].username, username) == 0) {
            time_t current_time = time(NULL);
            if (difftime(current_time, active_clients[i].last_heartbeat) <= 3) {
                return 1;  // 活跃
            }
            // 如果心跳超时，则标记为不活跃
            memset(&active_clients[i], 0, sizeof(ActiveClient));
            return 0;  // 不活跃
        }
    }
    return 0;  // 未登录
}

// 记录接收到的消息
void display_msg_received(int client_port, const char *request_type, const char *username) {
    printf("Received %s from %s at port %d\n", request_type, username, client_port);
}

// 记录发送的消息
void display_msg_sent(int client_port, const char *response_type, const char *username) {
    printf("Sent %s to %s at port %d\n", response_type, username, client_port);
}

// 发送响应
void send_response(int sockfd, struct sockaddr_in *client_addr, socklen_t client_len, const char *response_type, const char *response_content, int client_port, const char *username) {
    char response[MAX_BUFFER];
    snprintf(response, sizeof(response), "%s %s", response_type, response_content);
    sendto(sockfd, response, strlen(response), 0, (struct sockaddr *)client_addr, client_len);
    display_msg_sent(client_port, response_type, username);
}

// 处理 AUTH 请求
void handle_AUTH(int sockfd, struct sockaddr_in *client_addr, socklen_t client_len, const char *username, const char *password, int client_port) {
    display_msg_received(client_port, "AUTH", username);

    if (check_active(username)) {
        send_response(sockfd, client_addr, client_len, "ERR", "", client_port, username);
    } else if (check_credentials(username, password)) {
        for (int i = 0; i < num_clients; i++) {
            if (strcmp(active_clients[i].username, username) == 0) {
                active_clients[i].last_heartbeat = time(NULL);
                send_response(sockfd, client_addr, client_len, "OK", "", client_port, username);
                return;
            }
        }

        // 如果用户未登录，则添加到活动客户端列表中
        strncpy(active_clients[num_clients].username, username, MAX_BUFFER);
        active_clients[num_clients].last_heartbeat = time(NULL);
        num_clients++;
        send_response(sockfd, client_addr, client_len, "OK", "", client_port, username);
    } else {
        send_response(sockfd, client_addr, client_len, "ERR", "", client_port, username);
    }
}

// 处理 HBT 请求
void handle_HBT(const char *username) {
    for (int i = 0; i < num_clients; i++) {
        if (strcmp(active_clients[i].username, username) == 0) {
            active_clients[i].last_heartbeat = time(NULL);
            break;
        }
    }
}

// 处理 LAP 请求
void handle_LAP(int sockfd, struct sockaddr_in *client_addr, socklen_t client_len, int client_port) {
    display_msg_received(client_port, "LAP", "unknown");

    int active_count = 0;
    char response_content[MAX_BUFFER] = "";
    for (int i = 0; i < num_clients; i++) {
        if (check_active(active_clients[i].username)) {
            active_count++;
            strncat(response_content, active_clients[i].username, MAX_BUFFER - strlen(response_content) - 1);
            strncat(response_content, " ", MAX_BUFFER - strlen(response_content) - 1);
        }
    }

    char result[MAX_BUFFER];
    snprintf(result, sizeof(result), "%d %s", active_count, response_content);
    send_response(sockfd, client_addr, client_len, "OK", result, client_port, "unknown");
}

// 处理 LPF 请求
void handle_LPF(int sockfd, struct sockaddr_in *client_addr, socklen_t client_len, const char *username, int client_port) {
    display_msg_received(client_port, "LPF", username);

    int file_count = 0;
    char response_content[MAX_BUFFER] = "";
    for (int i = 0; i < num_published_files; i++) {
        if (strcmp(published_files[i].owner, username) == 0) {
            file_count++;
            strncat(response_content, published_files[i].filename, MAX_BUFFER - strlen(response_content) - 1);
            strncat(response_content, " ", MAX_BUFFER - strlen(response_content) - 1);
        }
    }

    char result[MAX_BUFFER];
    snprintf(result, sizeof(result), "%d %s", file_count, response_content);
    send_response(sockfd, client_addr, client_len, "OK", result, client_port, username);
}

// 处理 PUB 请求
void handle_PUB(int sockfd, struct sockaddr_in *client_addr, socklen_t client_len, const char *username, const char *filename, int client_port) {
    display_msg_received(client_port, "PUB", username);

    strncpy(published_files[num_published_files].filename, filename, MAX_BUFFER);
    strncpy(published_files[num_published_files].owner, username, MAX_BUFFER);
    num_published_files++;

    send_response(sockfd, client_addr, client_len, "OK", "", client_port, username);
}

// 处理 UNP 请求
void handle_UNP(int sockfd, struct sockaddr_in *client_addr, socklen_t client_len, const char *username, const char *filename, int client_port) {
    display_msg_received(client_port, "UNP", username);

    for (int i = 0; i < num_published_files; i++) {
        if (strcmp(published_files[i].filename, filename) == 0 && strcmp(published_files[i].owner, username) == 0) {
            memset(&published_files[i], 0, sizeof(PublishedFile));
            send_response(sockfd, client_addr, client_len, "OK", "", client_port, username);
            return;
        }
    }
    send_response(sockfd, client_addr, client_len, "ERR", "", client_port, username);
}


int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <port>\n", argv[0]);
        exit(EXIT_FAILURE);
    }

    int server_port = atoi(argv[1]);
    int sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0) {
        perror("socket failed");
        exit(EXIT_FAILURE);
    }

    struct sockaddr_in server_addr, client_addr;
    socklen_t client_len = sizeof(client_addr);
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(server_port);

    if (bind(sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("bind failed");
        close(sockfd);
        exit(EXIT_FAILURE);
    }

    load_credentials("credentials.txt");

    char buffer[MAX_BUFFER];
    while (1) {
        int n = recvfrom(sockfd, buffer, MAX_BUFFER, 0, (struct sockaddr *)&client_addr, &client_len);
        if (n < 0) {
            perror("recvfrom failed");
            continue;
        }
        buffer[n] = '\0';

        char request_type[10], username[50], password[50], filename[100];
        sscanf(buffer, "%s %s %s", request_type, username, password);
        int client_port = ntohs(client_addr.sin_port);

        if (strcmp(request_type, "AUTH") == 0) {
            handle_AUTH(sockfd, &client_addr, client_len, username, password, client_port);
        } else if (strcmp(request_type, "HBT") == 0) {
            handle_HBT(username);
        } else if (strcmp(request_type, "LAP") == 0) {
            handle_LAP(sockfd, &client_addr, client_len, client_port);
        } else if (strcmp(request_type, "LPF") == 0) {
            handle_LPF(sockfd, &client_addr, client_len, username, client_port);
        } else if (strcmp(request_type, "PUB") == 0) {
            sscanf(buffer, "%s %s %s", request_type, username, filename);
            handle_PUB(sockfd, &client_addr, client_len, username, filename, client_port);
        } else if (strcmp(request_type, "UNP") == 0) {
            sscanf(buffer, "%s %s %s", request_type, username, filename);
            handle_UNP(sockfd, &client_addr, client_len, username, filename, client_port);
        }
    }

    close(sockfd);
    return 0;
}
