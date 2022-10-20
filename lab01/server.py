"""
    Server
    Lab 01 Murashko Artem
"""

from enum import Enum
import signal
import time
import socket
import sys

# Config

server_port = 12300
udp_socket = None

sessions = dict()

# Constants

HOST = 'localhost'

NUMBER_OF_RETRIES = 5
TIMOUT = 0.5
BUFFER_SIZE = 1024
INACTIVITY_TIME = 3


class HashMapKey(Enum):
    file = 'file'
    file_name = 'file_name'
    file_size = 'file_size'
    last_active = 'last_active'
    sequence_number = 'sequence_number'


# Helper functions


def terminate(message):
    log(message)
    sys.exit()


def log(message):
    print(message)


# Server functions

# UDP Socket configuration

def create_udp_socket():
    global udp_socket

    try:
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.bind((HOST, server_port))
        udp_socket.settimeout(TIMOUT)
    except socket.error as error:
        terminate(f"Socket creation error {error}")

    log("Socket created")


# Communication


def start_server():
    global sessions

    while True:
        check_finished_sessions()
        terminate_inactive_sessions()

        try:
            client_message, client_address = udp_socket.recvfrom(BUFFER_SIZE)
            message_type = client_message[:1].decode()
        except KeyboardInterrupt as keys:
            terminate(f'{keys} was pressed, terminating server')
        except:
            continue

        handle_message(message_type, client_message, client_address)


def check_finished_sessions():
    for host in list(sessions.keys()):

        file = sessions[host][HashMapKey.file]
        file_name = sessions[host][HashMapKey.file_name]
        file_size = sessions[host][HashMapKey.file_size]
        last_active = sessions[host][HashMapKey.last_active]

        if time.time() - last_active >= 1 and len(file) == file_size:
            sessions.pop(host)

            with open(f'{file_name}', 'wb+') as output:
                output.write(file)

            log(f"Successfully received from host {host}")


def terminate_inactive_sessions():
    for host in list(sessions.keys()):
        if time.time() - sessions[host][HashMapKey.last_active] < INACTIVITY_TIME:
            continue

        sessions.pop(host)
        log(f"Host {host} is inactive, abandon the session")


def handle_message(message_type, client_message, client_address):
    def new_session(message, addr):
        desc, sequence_number, file_name, total_size = message.split(' | ')
        reply = f'a | {int(sequence_number) + 1} | {BUFFER_SIZE}'
        udp_socket.sendto(reply.encode(), addr)

        sessions[addr[1]] = {
            HashMapKey.file: b'',
            HashMapKey.file_name: file_name,
            HashMapKey.file_size: int(total_size),
            HashMapKey.last_active: time.time(),
            HashMapKey.sequence_number: int(sequence_number) + 1
        }

        log(f"New session with host {client_address[1]}")

    def existing_session(message, addr):
        first_sep = list(message).index(124)  # first separator
        second_sep = list(message).index(124, first_sep + 1)  # second separator

        sessions[addr[1]][HashMapKey.last_active] = time.time()
        sequence_number = int(message[first_sep + 1: second_sep])
        data = message[second_sep + 2:]
        if sequence_number == sessions[addr[1]][HashMapKey.sequence_number]:
            sessions[addr[1]][HashMapKey.sequence_number] = sequence_number + 1
            sessions[addr[1]][HashMapKey.file] += data

            ack_message = f'a | {sequence_number + 1}'
            udp_socket.sendto(ack_message.encode(), addr)

    if message_type == 's':
        new_session(client_message.decode(), client_address)
    elif message_type == 'd':
        existing_session(client_message, client_address)
    else:
        log("Unknown message type")


# Parsing

def parse_console_input():
    if len(sys.argv) != 2:
        terminate("Specify arguments in the following order: \n \
                  python3 server.py port")

    global server_port
    server_port = int(sys.argv[1])


# Main


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.default_int_handler)

    parse_console_input()
    create_udp_socket()

    start_server()
