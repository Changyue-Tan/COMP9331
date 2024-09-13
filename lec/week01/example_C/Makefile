# Compiler
CC = gcc

# Compiler flags
CFLAGS = -g -fsanitize=address,leak,undefined

# Output program name
OUTPUT = TCPClient TCPServer UDPClient UDPServer

# Source files
SRC = TCPClient.c TCPServer.c UDPClient.c UDPServer.c

# Default target
all: $(OUTPUT)

# Rule to compile the program
$(OUTPUT): $(SRC)
	$(CC) $(CFLAGS) -o $(OUTPUT) $(SRC)

# Clean up object files and executable
clean:
	rm -f $(OUTPUT)
