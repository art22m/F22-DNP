import socket
import sys
import signal

# Constants

BUFFER_SIZE = 1024

# Config

server_address = ("127.0.0.1", 12300)
client_name = 'Default_name'
tcp_socket = None


# Helper functions


def terminate(message):
    print(message)
    sys.exit()


# Client functions


def create_tcp_socket():
    global tcp_socket

    try:
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.connect(server_address)
    except socket.error as error:
        terminate(f"Socket creation error: {error}")

    print("Socket created")


def start_client():
    create_tcp_socket()

    try:
        tcp_socket.sendall(client_name.encode())
    except:
        terminate("Server closed the connection")

    while True:
        try:
            data = tcp_socket.recv(BUFFER_SIZE)

            if not data:
                tcp_socket.close()
                terminate("Server closed the connection")

            print(data.decode(), end='')
        except KeyboardInterrupt as keys:
            tcp_socket.close()
            terminate(f'{keys} was pressed, terminating client')


# Parsing

def parse_console_input():
    if len(sys.argv) != 3:
        terminate("Specify arguments in the following order: \n \
                  python3 client.py server_ip:server_port name")

    global server_address

    address = sys.argv[1].split(":")
    server_address = (address[0], int(address[1]))

    global client_name

    client_name = sys.argv[2]


# Main


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.default_int_handler)

    parse_console_input()

    try:
        start_client()
    except KeyboardInterrupt as keys:
        terminate(f'{keys} was pressed, terminating server')
