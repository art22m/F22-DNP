import service_pb2 as pb2
import service_pb2_grpc as pb2_grpc

import grpc
import sys
import signal

# Config

HOST = '127.0.0.1'
PORT = '5555'

channel = None
stub = None


# Helper functions


def terminate(message):
    log(message)
    sys.exit()


def log(message, end="\n"):
    print(message, end=end)


# Client

def request_reverse(text):
    msg = pb2.TextReq(text=text)
    response = stub.ReverseText(msg)

    log("reversed: " + response.text)


def request_split(text):
    msg = pb2.SplitTextReq(text=text, delim=' ')
    response = stub.SplitText(msg)

    log(f"count: {response.count}")
    for part in response.parts:
        log("part: " + part)


def request_is_prime(text):
    def generate_requests(text):
        for number in text.split(' '):
            try:
                yield pb2.NumberReq(number=int(number))
            except:
                continue

    for response in stub.IsPrime(generate_requests(text)):
        log(response.text)


def start_client():
    global channel
    global stub

    channel = grpc.insecure_channel(f"{HOST}:{PORT}")
    stub = pb2_grpc.InnoServiceStub(channel)

    while True:
        try:
            input_text = input()

            try:
                command = input_text.split(" ")[0]
                argument = input_text.split(maxsplit=1)[1]
            except:
                if command == "exit":
                    terminate("Exit command, terminating client")

                log("Invalid command")
                continue

            if command == "reverse":
                request_reverse(argument)
            elif command == "split":
                request_split(argument)
            elif command == "isprime":
                request_is_prime(argument)
            else:
                log("Unknown command")
        except KeyboardInterrupt as keys:
            terminate(f'{keys} was pressed, terminating client')


# Parsing


def parse_arguments():
    if len(sys.argv) != 2:
        terminate("Specify arguments in the following order: \n \
                  python3 client.py HOST:PORT")

    global HOST
    global PORT

    try:
        arg = sys.argv[1].split(":")
        HOST = arg[0]
        PORT = int(arg[1])
    except:
        terminate("Specify arguments in the following order: \n \
                          python3 client.py HOST:PORT")

# Main


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.default_int_handler)

    parse_arguments()

    try:
        start_client()
    except KeyboardInterrupt as keys:
        terminate(f'{keys} was pressed, terminating client')
