import threading
import time

# Placeholder function for heartbeat mechanism (runs in a separate thread)
def send_heartbeat():
    while True:
        print("Sending heartbeat to server...")
        time.sleep(2)  # Simulates sending a heartbeat every 2 seconds

# Function to handle user commands
def handle_commands():
    print("Welcome to BitTrickle!")
    print("Available commands are: get, lap, lpf, pub, sch, unp, xit")

    while True:
        command = input("> ").strip()

        if command.startswith("get "):
            filename = command.split(" ")[1]
            print(f"Attempting to get file '{filename}' from active peers...")

        elif command == "lap":
            print("Listing all active peers...")

        elif command == "lpf":
            print("Listing all published files by this user...")

        elif command.startswith("pub "):
            filename = command.split(" ")[1]
            print(f"Publishing file '{filename}'...")

        elif command.startswith("sch "):
            substring = command.split(" ")[1]
            print(f"Searching for files containing '{substring}'...")

        elif command.startswith("unp "):
            filename = command.split(" ")[1]
            print(f"Unpublishing file '{filename}'...")

        elif command == "xit":
            print("Exiting BitTrickle...")
            break

        else:
            print("Unknown command. Please try again.")

# Main function to start the client UI
def main():
    # Start the heartbeat mechanism in a separate thread
    heartbeat_thread = threading.Thread(target=send_heartbeat)
    heartbeat_thread.daemon = True  # Daemon thread will exit when the main thread exits
    heartbeat_thread.start()

    # Handle user commands in the main thread
    handle_commands()

if __name__ == "__main__":
    main()
