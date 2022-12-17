import zmq
import sys
import signal

from time import sleep

# Config

HOST = '127.0.0.1'

CLIENT_NAME = 'test1'

SERVER_WRITER_PORT = '5001'


# Helper functions

def terminate(message):
    print(message)
    sys.exit()


# Client functions

def start_client():
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.connect(f"tcp://{HOST}:{SERVER_WRITER_PORT}")
    socket.setsockopt(zmq.RCVTIMEO, 400)

    while True:
        message = str(input())
        try:
            socket.send_string(f"{CLIENT_NAME}|{message}")

        except:
            terminate("Sever is no responding. Terminating.")


# Parsing


def parse_arguments():
    if len(sys.argv) != 3:
        terminate("Specify arguments in the following order: \n \
                  python3 writer_client.py SERVER_WRITER_PORT name")

    global SERVER_WRITER_PORT
    SERVER_WRITER_PORT = int(sys.argv[1])

    global CLIENT_NAME
    CLIENT_NAME = sys.argv[2]


# Main


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.default_int_handler)

    parse_arguments()

    try:
        start_client()
    except KeyboardInterrupt as keys:
        terminate(f'{keys} was pressed, terminating client')
