import zmq
import sys
import signal

from threading import Thread
from time import sleep

# Config

HOST = 'localhost'

SERVER_INPUT_PORT = '5556'
SERVER_OUTPUT_PORT = '5555'

SERVER_TIMOUT = 5000  # milliseconds

server_input_socket = None


# Helper functions


def terminate(message):
    log(message)
    sys.exit()


def log(message, end="\n"):
    print(message, end=end)


# Server functions

def connect_server_output():
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(f"tcp://{HOST}:{SERVER_OUTPUT_PORT}")
    socket.setsockopt_string(zmq.SUBSCRIBE, '')
    socket.RCVTIMEO = SERVER_TIMOUT

    while True:
        try:
            message = socket.recv_string()
            log(message)
        except:
            continue


def send_to_server(message):
    global server_input_socket

    if server_input_socket is None:
        context = zmq.Context()
        server_input_socket = context.socket(zmq.REQ)
        server_input_socket.connect(f"tcp://{HOST}:{SERVER_INPUT_PORT}")
        server_input_socket.RCVTIMEO = SERVER_TIMOUT
        sleep(1)

    try:
        server_input_socket.send_string(message)
        server_input_socket.recv()  # needs to prevent deadlock
    except:
        terminate("Sever is no responding. Terminating.")


def start_client():
    server_output_thread = Thread(target=connect_server_output, args=(), daemon=True)
    server_output_thread.start()
    while True:
        message = str(input())
        send_to_server(message)


# Parsing


def parse_arguments():
    if len(sys.argv) != 3:
        terminate("Specify arguments in the following order: \n \
                  python3 gcd.py SERVER_OUTPUT_PORT SERVER_INPUT_PORT")

    global SERVER_INPUT_PORT
    global SERVER_OUTPUT_PORT

    SERVER_OUTPUT_PORT = int(sys.argv[1])
    SERVER_INPUT_PORT = int(sys.argv[2])


# Main


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.default_int_handler)

    parse_arguments()

    try:
        start_client()
    except KeyboardInterrupt as keys:
        terminate(f'{keys} was pressed, terminating client')
