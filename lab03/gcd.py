import zmq
import sys
import signal

from time import sleep

# Config

HOST = '127.0.0.1'
INPUT_PORT = '5557'
OUTPUT_PORT = '5558'

output_socket = None


# Helper functions


def terminate(message):
    log(message)
    sys.exit()


def log(message):
    print(message)


# Worker functions


def find_gcd(first_number, second_number):
    x = abs(first_number)
    y = abs(second_number)

    if x == 0 and y == 0:
        send_output(f"gcd for {first_number} and {second_number} is not defined")
        return

    if x == 0:
        send_output(f"gcd for {first_number} and {second_number} is {second_number}")
        return

    if y == 0:
        send_output(f"gcd for {first_number} and {second_number} is {first_number}")
        return

    # Euclidian algorithm
    while y:
        x, y = y, x % y
    gcd = abs(x)

    send_output(f"gcd for {first_number} and {second_number} is {gcd}")


def connect_input():
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(f"tcp://{HOST}:{INPUT_PORT}")
    socket.setsockopt_string(zmq.SUBSCRIBE, '')

    while True:
        try:
            message = socket.recv_string()
            data = message.split(" ")
            if len(data) != 3 or data[0] != "gcd":
                continue
            log(f"Request: Find gcd for {data[1]} and {data[2]}.")
            find_gcd(int(data[1]), int(data[2]))
        except KeyboardInterrupt as keys:
            terminate(f'{keys} was pressed, terminating gcd')
        except:
            continue


def send_output(message):
    log("Sending <" + message + ">")
    global output_socket
    if output_socket is None:
        context = zmq.Context()
        output_socket = context.socket(zmq.PUB)
        output_socket.connect(f"tcp://{HOST}:{OUTPUT_PORT}")
        sleep(1)

    output_socket.send_string(message)


def start_gcd():
    connect_input()


# Parsing


def parse_arguments():
    if len(sys.argv) != 3:
        terminate("Specify arguments in the following order: \n \
                  python3 gcd.py INPUT_PORT OUTPUT_PORT")

    global INPUT_PORT
    global OUTPUT_PORT

    INPUT_PORT = int(sys.argv[1])
    OUTPUT_PORT = int(sys.argv[2])


# Main


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.default_int_handler)

    parse_arguments()

    try:
        start_gcd()
    except KeyboardInterrupt as keys:
        terminate(f'{keys} was pressed, terminating gcd')
