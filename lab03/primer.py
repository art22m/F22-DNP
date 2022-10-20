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


def is_prime(number):
    if number <= 0:
        send_output(f"{number} is not prime")
        return

    prime = True
    for divisor in range(2, number):
        if divisor * divisor > number:
            break

        if number % divisor == 0:
            prime = False
            break

    if prime:
        send_output(f"{number} is prime")
    else:
        send_output(f"{number} is not prime")


def connect_input():
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(f"tcp://{HOST}:{INPUT_PORT}")
    socket.setsockopt_string(zmq.SUBSCRIBE, '')

    while True:
        try:
            message = socket.recv_string()
            data = message.split(" ")
            if len(data) != 2 or data[0] != "isprime":
                continue
            log(f"Request: Determine is {data[1]} prime number.")
            is_prime(int(data[1]))
        except KeyboardInterrupt as keys:
            terminate(f'{keys} was pressed, terminating primer')
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



def start_primer():
    connect_input()


# Parsing


def parse_arguments():
    if len(sys.argv) != 3:
        terminate("Specify arguments in the following order: \n \
                  python3 primer.py INPUT_PORT OUTPUT_PORT")

    global INPUT_PORT
    global OUTPUT_PORT

    INPUT_PORT = int(sys.argv[1])
    OUTPUT_PORT = int(sys.argv[2])


# Main


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.default_int_handler)

    parse_arguments()

    try:
        start_primer()
    except KeyboardInterrupt as keys:
        terminate(f'{keys} was pressed, terminating primer')
