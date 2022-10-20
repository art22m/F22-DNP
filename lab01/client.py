"""
    Client
    Lab 01 Murashko Artem
"""

import signal
import os.path
import socket
import sys

# Logging variables

chunk_number = 1
prev_number_of_percentage = 0

# Config

server_address = None
file_path = None
filename_on_server = None
file_size = None

udp_socket = None

sequence_number = None
buffer_size = None

# Constants

NUMBER_OF_RETRIES = 5
TIMOUT = 0.5
CLIENT_BUFFER_SIZE = 1024


# Helper functions


def terminate(message):
    log(message)
    sys.exit()


def log(message):
    print(message)


def log_transfer_percentage(current_message_size):
    global chunk_number
    global prev_number_of_percentage

    transfer_percentage = int(abs(buffer_size - current_message_size) * chunk_number / file_size * 100)
    if transfer_percentage % 10 == 0 and prev_number_of_percentage != transfer_percentage:
        log(f"Transferred about {transfer_percentage}%")
        prev_number_of_percentage = transfer_percentage
    chunk_number += 1


# Client functions

# UDP Socket configuration


def create_udp_socket():
    global udp_socket

    try:
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.settimeout(TIMOUT)
    except socket.error:
        terminate("Socket creation error")

    log("Socket created")


# Communication


def send_start_message():
    start_message = f"s | 0 | {filename_on_server} | {file_size}"

    attempts_counter = 0
    while attempts_counter < NUMBER_OF_RETRIES:
        attempts_counter += 1

        udp_socket.sendto(start_message.encode(), server_address)

        try:
            response, address = udp_socket.recvfrom(CLIENT_BUFFER_SIZE)
            parse_start_ack_message(response)
            break
        except KeyboardInterrupt as keys:
            terminate(f'{keys} was pressed, terminating client')
        except:
            continue

    else:
        terminate("Server is malfunctioning, terminate")


def send_file():
    global sequence_number

    with open(file_path, 'rb') as file:
        while True:
            message = f"d | {sequence_number} | ".encode()
            current_message_size = len(message)

            data = file.read(abs(buffer_size - current_message_size))
            if not data:
                terminate("Successfully transmitted a file")

            message += data
            log_transfer_percentage(current_message_size)

            attempts_counter = 0
            while attempts_counter < NUMBER_OF_RETRIES:
                attempts_counter += 1

                udp_socket.sendto(message, server_address)
                try:
                    response, address = udp_socket.recvfrom(CLIENT_BUFFER_SIZE)
                    parse_ack_message(response)
                    break
                except KeyboardInterrupt as keys:
                    terminate(f'{keys} was pressed, terminating client')
                except:
                    log(f"Retry... seqNo={sequence_number}")
                    continue
            else:
                terminate("Server is malfunctioning, terminate session")


# Parsing


def parse_console_input():
    if len(sys.argv) != 4:
        terminate("Specify arguments in the following order: \n \
                  python3 client.py server-hostname:port file_path filename_on_server")

    global server_address
    global file_path
    global filename_on_server
    global file_size

    address = sys.argv[1].split(":")
    server_address = (address[0], int(address[1]))
    file_path = sys.argv[2]
    filename_on_server = sys.argv[3]
    file_size = os.path.getsize(file_path)


def parse_start_ack_message(message):
    parameters = message.decode().split(" | ")
    if len(parameters) != 3:
        terminate("Incorrect format of ack message")

    if parameters[0] != 'a':
        terminate("Receive not ack message")

    global sequence_number
    sequence_number = int(parameters[1])

    global buffer_size
    buffer_size = int(parameters[2])


def parse_ack_message(message):
    parameters = message.decode().split(" | ")
    if len(parameters) != 2:
        terminate("Incorrect format of ack message")

    if parameters[0] != 'a':
        terminate("Receive not ack message")

    global sequence_number
    sequence_number = int(parameters[1])


# Main


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.default_int_handler)

    parse_console_input()
    create_udp_socket()

    send_start_message()
    send_file()
