import socket
import time
from datetime import datetime
import threading
import sys

# Authentication
# load credentials file
def load_credentials():
    credentials = {}
    with open('credentials.txt', 'r') as file:
        for line in file:
            username, password = line.strip().split(' ')
            credentials[username] = password
    return credentials

# Heartbeat mechanism
active_account = {}  #  {username: (last_active_time, client_addr)}
def check_heartbeat():
    while True:
        cur_time = time.time()
        inactive_account = [user for user, (last_heartbeat, _) in active_account.items()
                          if cur_time - last_heartbeat > 3]
        # remove the inactive ones
        for user in inactive_account:
            del active_account[user]

        time.sleep(1)

def handle_heartbeat(username, address):
    cur_time = time.time()
    active_account[username] = (cur_time, address)


pub_files = {}  # store published files
users_pub = {}  # store someone's publishment

# Handle client request
def handle_request(data, client_addr, credentials, server_socket):
    global active_account
    sent = 'OK'
    # data = 'command + request + content'
    msg = data.split(' ', 2)
    command = msg[0]
    username = msg[1]
    element = msg[2] if len(msg) > 2 else None

    # authentication
    if command == "AUTH":
        # data = AUTH + USERNAME + PASSWORD

        password = element
        if username in credentials.keys() and credentials[username] == password:
            if username not in active_account.keys():
                handle_heartbeat(username, client_addr)
                response = "Welcome to BitTrickle!"
            else:
                response = "Authentication failed. Please try again."
                sent = 'ERR'
        else:
            response = "Authentication failed. Please try again."
            sent = 'ERR'

        server_socket.sendto(response.encode(), client_addr)

    # heartbeat mechanism
    elif command == "HBT":
        if username in active_account:
            handle_heartbeat(username, client_addr)
            # new_lastAT = time.time()
            # active_account[request] = (new_lastAT, active_account[request][1])

    # define clients' command
    elif command == "GET":
        # data = 'GET + USERNAME + FILENAME'
        filename = element

        if filename in pub_files:
            for publisher_username in pub_files[filename]:
                if publisher_username in active_account:
                    publisher_addr = active_account[publisher_username][1]
                    # choose the first one active
                    response = f"EXIST {publisher_addr[0]} {publisher_addr[1]}"
                    break

            else:
                response = "File not found."
                sent = "ERR"
        else:
            response = "File not found."
            sent = "ERR"

        server_socket.sendto(response.encode(), client_addr)

    elif command == "LAP":
        # find active peers not include itself
        # data = 'LAP + USERNAME'

        active_peers = [user for user in active_account if user != username]
        length = len(active_peers)

        if active_peers:
            if length == 1:
                response = "1 active peers:\n" + active_peers[0]
            else:
                response = f"{length} active peers:\n" + "\n".join(active_peers)
        else:
            response = "No active peers."

        server_socket.sendto(response.encode(), client_addr)

    elif command == "LPF":
        # print user's file
        # data = 'LPF + USERNAME'

        if username in users_pub and users_pub[username]:
            length = len(users_pub[username])
            if length == 1:
                response = "1 file published:\n" + users_pub[username][0]
            else:
                response = f"{length} file published:\n" + "\n".join(users_pub[username])
        else:
            response = "No files published."

        server_socket.sendto(response.encode(), client_addr)

    elif command == "PUB":
        # publish a file (maybe has been published)
        # data = 'PUB + USERNAME + FILENAME'
        filename = element

        if filename not in pub_files:
            pub_files[filename] = [] # {filename: [user1, user2, ...]}
        if username not in pub_files[filename]:
            pub_files[filename].append(username)

        if username not in users_pub:
            users_pub[username] = [] # {username: [file1, file2, ...]}
        if filename not in users_pub[username]:
            users_pub[username].append(filename)

        response = "File published successfully."
        server_socket.sendto(response.encode(), client_addr)

    elif command == "SCH":
        # search files which are not published by user
        # data = 'SCH + USERNAME + str'

        matching_file = []
        for filename in pub_files:
            if element in filename and filename not in users_pub[username]:
                matching_file.append(filename)

        if matching_file:
            length = len(matching_file)
            if length == 1:
                response = "1 file found:\n" + matching_file[0]
            else:
                response = f"{length} files found:\n " + "\n".join(matching_file)
        else:
            response = "File not found."
            sent = 'ERR'

        server_socket.sendto(response.encode(), client_addr)

    elif command == "UNP":
        # cancel publishment (if has another authors?)
        # data = 'UNP + USERNAME + FILENAME'
        filename = element

        if filename in pub_files and username in pub_files[filename]:
            if len(pub_files[filename]) == 1:
                del pub_files[filename]
                users_pub[username].remove(filename)

                response = "File unpublished successfully."
            else:
                pub_files[filename].remove(username)
                users_pub[username].remove(filename)

                response = "File unpublished successfully."
        else:
            response = "File unpublished failed."
            sent = 'ERR'

        server_socket.sendto(response.encode(), client_addr)

    # sent message
    elif command != "HBT":
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        client_port = client_address[1]
        print(f"{timestamp}: {client_port}: Sent {sent} to {username}")

    else:
        # error command
        response = "Error command."
        server_socket.sendto(response.encode(), client_addr)

# Start server
def start_server(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(("127.0.0.1", port))
    print("Server started on port: ", port)

    credentials = load_credentials()
    threading.Thread(target=check_heartbeat, daemon=True).start()

    while True:
        data, client_addr = server_socket.recvfrom(1024)
        handle_request(data.decode(), client_addr, credentials, server_socket)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python server.py <port>")
        sys.exit(1)