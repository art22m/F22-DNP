import zmq
import sys
import signal
import time

from threading import Thread

# Config

HOST = '127.0.0.1'
WRITER_PORT = '5001'
READER_PORT = '5002'

DURATION = 5.0

clients_reader_socket = None

messages = {}
last_time = 0

# Helper functions


def terminate(message):
    print(message)
    sys.exit()


# Server functions

def send_to_reader():
    global clients_reader_socket
    if clients_reader_socket is None:
        context = zmq.Context()
        clients_reader_socket = context.socket(zmq.PUB)
        clients_reader_socket.bind(f"tcp://{HOST}:{READER_PORT}")

        time.sleep(1)

    message = 'SUMMARY\n'
    for name, value in sorted(messages.items()):
        message += f" {name}: {value}\n"

    clients_reader_socket.send_string(message)

    global last_time
    last_time = time.time()

    for name in messages.keys():
        messages[name] = 0


def start_server():
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.bind(f"tcp://{HOST}:{WRITER_PORT}")
    socket.setsockopt_string(zmq.SUBSCRIBE, '')
    socket.RCVTIMEO = 100

    global last_time
    global DURATION
    last_time = time.time()

    while True:
        try:
            message = socket.recv_string()
            # save to dict
            name = message.split("|")[0]
            try:
                messages[name] += 1
            except:
                messages[name] = 1

        except KeyboardInterrupt as keys:
            terminate(f'{keys} was pressed, terminating primer')

        except:
            if time.time() > last_time + DURATION:
                send_to_reader()
            continue


# Parsing


def parse_arguments():
    if len(sys.argv) != 3:
        terminate("Specify arguments in the following order: \n \
                  python3 gcd.py WRITER_PORT READER_PORT")

    global WRITER_PORT
    WRITER_PORT = int(sys.argv[1])

    global READER_PORT
    READER_PORT = int(sys.argv[2])


# Main


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.default_int_handler)

    parse_arguments()

    try:
        start_server()
    except KeyboardInterrupt as keys:
        terminate(f'{keys} was pressed, terminating server')
