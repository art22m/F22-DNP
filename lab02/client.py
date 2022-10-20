"""
    Client
    Lab 02 Murashko Artem
"""

import socket
import sys
import signal

# Constants

BUFFER_SIZE = 1024
TIMOUT = 5.0


# Config

server_address = ("127.0.0.1", 12300)
tcp_socket = None


# Helper functions


def terminate(message):
    log(message)
    sys.exit()


def log(message):
    print(message)


# Client functions


def create_tcp_socket():
    global tcp_socket

    try:
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.settimeout(TIMOUT)
        tcp_socket.connect(server_address)
    except socket.error as error:
        terminate(f"Socket creation error: {error}")

    log("Socket created")


def start_client():
    create_tcp_socket()

    numbers = [15492781, 15492787, 15492803,
               15492811, 15492810, 15492833,
               15492859, 15502547, 15520301,
               15527509, 15522343, 1550784]

    for number in numbers:
        try:
            tcp_socket.sendall(f"{number}".encode())
            data = tcp_socket.recv(BUFFER_SIZE)

            if not data:
                log("Server closed the connection")
                tcp_socket.close()
                return

            log(data.decode())
        except KeyboardInterrupt as keys:
            tcp_socket.close()
            terminate(f'{keys} was pressed, terminating client')
        except:
            terminate("Server closed the connection")
            continue

    tcp_socket.close()
    log("Completed")


# Parsing

def parse_console_input():
    if len(sys.argv) != 2:
        terminate("Specify arguments in the following order: \n \
                  python3 client.py server-hostname:port")

    global server_address

    address = sys.argv[1].split(":")
    server_address = (address[0], int(address[1]))


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.default_int_handler)

    parse_console_input()
    start_client()
