import zmq
import sys
import signal
from time import sleep

from threading import Thread

# Config

HOST = '127.0.0.1'

WORKERS_INPUT_PORT = '5557'
WORKERS_OUTPUT_PORT = '5558'

workers_input_socket = None

CLIENTS_INPUT_PORT = '5555'
CLIENTS_OUTPUT_PORT = '5556'

clients_input_socket = None


# Helper functions


def terminate(message):
    log(message)
    sys.exit()


def log(message, end="\n"):
    print(message, end=end)


# Server functions

def send_to_clients(message):
    global clients_input_socket

    if clients_input_socket is None:
        context = zmq.Context()
        clients_input_socket = context.socket(zmq.PUB)
        clients_input_socket.bind(f"tcp://{HOST}:{CLIENTS_INPUT_PORT}")
        sleep(1)

    clients_input_socket.send_string(message)


def connect_workers_output():
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.bind(f"tcp://{HOST}:{WORKERS_OUTPUT_PORT}")
    socket.setsockopt_string(zmq.SUBSCRIBE, '')
    sleep(1)

    while True:
        try:
            message = socket.recv_string()
            log("Workers input: <" + message + ">")
            send_to_clients(message)
        except KeyboardInterrupt as keys:
            terminate(f'{keys} was pressed, terminating server')
        except:
            continue


def send_to_workers(message):
    global workers_input_socket
    if workers_input_socket is None:
        context = zmq.Context()
        workers_input_socket = context.socket(zmq.PUB)
        workers_input_socket.bind(f"tcp://{HOST}:{WORKERS_INPUT_PORT}")
        sleep(1)

    workers_input_socket.send_string(message)


def connect_clients_output():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://{HOST}:{CLIENTS_OUTPUT_PORT}")

    while True:
        try:
            message = socket.recv_string()
            socket.send_string("")  # needs to prevent deadlock
            log("Clients input: <" + message + ">")

            send_to_clients(message)
            send_to_workers(message)
        except KeyboardInterrupt as keys:
            terminate(f'{keys} was pressed, terminating server')
        except:
            continue


def start_server():
    workers_output_thread = Thread(target=connect_workers_output, args=(), daemon=True)
    workers_output_thread.start()

    clients_output_thread = Thread(target=connect_clients_output, args=(), daemon=True)
    clients_output_thread.start()

    # used to main thread not to be killed
    while True:
        continue


# Parsing


def parse_arguments():
    if len(sys.argv) != 5:
        terminate("Specify arguments in the following order: \n \
                  python3 gcd.py CLIENTS_INPUT_PORT CLIENTS_OUTPUT_PORT WORKERS_INPUT_PORT WORKERS_OUTPUT_PORT")

    global CLIENTS_INPUT_PORT
    global CLIENTS_OUTPUT_PORT
    global WORKERS_INPUT_PORT
    global WORKERS_OUTPUT_PORT

    CLIENTS_INPUT_PORT = int(sys.argv[1])
    CLIENTS_OUTPUT_PORT = int(sys.argv[2])
    WORKERS_INPUT_PORT = int(sys.argv[3])
    WORKERS_OUTPUT_PORT = int(sys.argv[4])


# Main


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.default_int_handler)

    parse_arguments()

    try:
        start_server()
    except KeyboardInterrupt as keys:
        terminate(f'{keys} was pressed, terminating server')
