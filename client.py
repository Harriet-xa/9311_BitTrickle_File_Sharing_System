import socket
import threading
import time
import sys
import os

USER = None  # clear which user
SERVER_ADDR = None
TCP_PORT = 9000

# heartbeat message
def send_HBT(client_socket, server_addr):
    while True:
        data = f"HBT {USER}"
        client_socket.sendto(data.encode(), server_addr)
        time.sleep(2)

def listen_to_server(client_socket):
    while True:
        response, _ = client_socket.recvfrom(1024)
        print(response.decode())
        # print(">", end='', flush=True)

def handle_command(command, client_socket, server_addr):
    parts = command.split(' ', 2)
    # msg = command + filename
    cmd = parts[0].upper()
    element = parts[1] if len(parts) > 1 else None

    if cmd == "GET":
        # data = 'GET + FILENAME'
        filename = element
        message = f"GET {USER} {filename}"
        client_socket.sendto(message.encode(), server_addr)

        # response, _ = client_socket.recvfrom(1024)
        # peer_info = response.decode()
        #
        # if peer_info == 'File not found.':
        #     print(peer_info)
        #
        # else:
        #     peer_ip, peer_port = peer_info.split()  # server return ip and port who has the file
        #     peer_addr = (peer_ip, int(peer_port))
        #     threading.Thread(target=download_file, args=(filename, peer_addr), daemon=True).start()

    elif cmd == "LAP":
        # data = 'LAP + USERNAME'
        message = f"LAP {USER}"
        client_socket.sendto(message.encode(), server_addr)

    elif cmd == "LPF":
        # data = 'LPF + USERNAME'
        message = f"LPF {USER}"
        client_socket.sendto(message.encode(), server_addr)

    elif cmd == "PUB":
        # data = 'PUB + USERNAME + FILENAME'
        filename = element
        if os.path.isfile(filename):
            message = f"PUB {USER} {filename}"
            client_socket.sendto(message.encode(), server_addr)
        else:
            print(f"File '{filename}' does not exist.")

    elif cmd == "SCH":
        # data = 'SCH + USERNAME + str'
        message = f"SCH {USER} {element}"
        client_socket.sendto(message.encode(), server_addr)

    elif cmd == "UNP":
        # data = 'UNP + USERNAME + FILENAME'
        filename = element
        message = f"UNP {USER} {filename}"
        client_socket.sendto(message.encode(), server_addr)

    elif cmd == "XIT":
        print("Goodbye!")
        client_socket.close()
        sys.exit(0)

    else:
        print("Invalid command. Please try again.")

    # print(">", end='', flush=True)


def download_file(filename, peer_addr):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
            tcp_socket.connect(peer_addr)
            tcp_socket.sendall(f"GET {filename}".encode())

            with open(filename, 'wb') as f:
                while True:
                    data = tcp_socket.recv(1024)
                    if not data:
                        break
                    f.write(data)

        print(f"File '{filename}' downloaded successfully.")

    except Exception as e:
        print(f"File '{filename}' downloaded failed: {e}.")


def listen_for_download_requests():
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind(('0.0.0.0', TCP_PORT))
    tcp_socket.listen(5)
    print(f"Listening for download requests on TCP port {TCP_PORT}")

    while True:
        conn, addr = tcp_socket.accept()
        threading.Thread(target=handle_download_request, args=(conn,), daemon=True).start()


def handle_download_request(conn):
    request = conn.recv(1024).decode()
    parts = request.split()
    if len(parts) == 2 and parts[0] == "GET":
        filename = parts[1]
        if os.path.isfile(filename):
            with open(filename, 'rb') as f:
                while True:
                    data = f.read(1024)
                    if not data:
                        break
                    conn.send(data)
        print(f"File '{filename}' sent to peer.")
    conn.close()


def start_client(port):
    global USER, SERVER_ADDR
    server_addr = ('127.0.0.1', port)
    SERVER_ADDR = server_addr
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # First AUTH
    while True:
        username = input("Enter username: ")
        password = input("Enter password: ")

        # data = AUTH + USERNAME + PASSWORD
        data = f"AUTH {username} {password}"
        client_socket.sendto(data.encode(), server_addr)

        response, _ = client_socket.recvfrom(1024)
        message = response.decode()
        print(message)

        # login successful
        if message == "Welcome to BitTrickle!":
            break

    USER = username

    # start heartbeat thread
    threading.Thread(target=send_HBT, args=(client_socket, server_addr), daemon=True).start()

    # listen to the server
    threading.Thread(target=listen_to_server, args=(client_socket,), daemon=True).start()

    # threading.Thread(target=start_file_server, daemon=True).start()

    print("Available commands are: get, lap, lpf, pub, sch, unp, xit\n")
    # print(">", end='', flush=True)

    while True:
        # print(">", end='', flush=True)
        command = input()  # > lap
        handle_command(command, client_socket, server_addr)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python client.py <port>")
        sys.exit(1)

    port = int(sys.argv[1])
    start_client(port)
