import service_pb2 as pb2
import service_pb2_grpc as pb2_grpc

import grpc
import signal
import sys

from concurrent import futures

# Config

HOST = '127.0.0.1'
PORT = '5555'

MAX_WORKERS = 10


# Helper functions


def terminate(message):
    log(message)
    sys.exit()


def log(message, end="\n"):
    print(message, end=end)


# Server

def is_prime(number):
    if number <= 1:
        return f"{number} is not prime"

    prime = True
    for divisor in range(2, number):
        if divisor * divisor > number:
            break

        if number % divisor == 0:
            prime = False
            break

    if prime:
        return f"{number} is prime"
    else:
        return f"{number} is not prime"


class InnoServiceHandler(pb2_grpc.InnoServiceServicer):
    # Returns reversed string
    def ReverseText(self, request, context):
        text = request.text
        reversed_text = text[::-1]

        return pb2.TextRep(text=reversed_text)

    # Splits the text by delimiter. Returns
    # number of parts and parts them self.
    def SplitText(self, request, context):
        text = request.text
        delim = request.delim

        split_text = text.split(delim)
        count = len(split_text)

        return pb2.SplitTextRep(count=count, parts=split_text)

    # Checks if number is prime or not. This is a stream
    # function, which means it accepts a stream of numbers and returns a stream of
    # answers.
    def IsPrime(self, request_iterator, context):
        for request in request_iterator:
            number = request.number
            yield pb2.TextRep(text=is_prime(number))


# Server functions


def start_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=MAX_WORKERS))
    pb2_grpc.add_InnoServiceServicer_to_server(InnoServiceHandler(), server)
    server.add_insecure_port(f"{HOST}:{PORT}")
    server.start()

    try:
        server.wait_for_termination()
    except KeyboardInterrupt as keys:
        terminate(f'{keys} was pressed, terminating server')


# Parsing


def parse_arguments():
    if len(sys.argv) != 2:
        terminate("Specify arguments in the following order: \n \
                  python3 server.py PORT")

    global PORT

    PORT = int(sys.argv[1])


# Main

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.default_int_handler)

    parse_arguments()

    try:
        start_server()
    except KeyboardInterrupt as keys:
        terminate(f'{keys} was pressed, terminating server')
