import zmq
import sys
import signal

# Config

HOST = '127.0.0.1'
SERVER_READER_PORT = '5002'

messages = {}  # {name : count}

timer = None


# Helper functions


def terminate(message):
    print(message)
    sys.exit()


# Client functions

def start_client():
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.setsockopt_string(zmq.SUBSCRIBE, '')
    socket.connect(f"tcp://{HOST}:{SERVER_READER_PORT}")

    while True:
        try:
            message = socket.recv_string()
            print(message)

        except KeyboardInterrupt as keys:
            terminate(f'{keys} was pressed, terminating client')

        except:
            continue


# Parsing


def parse_arguments():
    if len(sys.argv) != 2:
        terminate("Specify arguments in the following order: \n \
                  python3 reader_client.py SERVER_READER_PORT")

    global SERVER_READER_PORT
    SERVER_READER_PORT = int(sys.argv[1])


# Main


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.default_int_handler)

    parse_arguments()

    try:
        start_client()
    except KeyboardInterrupt as keys:
        terminate(f'{keys} was pressed, terminating client')
