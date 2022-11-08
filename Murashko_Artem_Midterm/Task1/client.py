import queue_pb2 as pb2
import queue_pb2_grpc as pb2_grpc


import grpc
import sys
import signal

# Config

HOST = '127.0.0.1'
PORT = '5555'

SERVER_CONNECTION_TIMEOUT = 1.5
SERVER_RESPONSE_TIMEOUT = 5

channel = None
stub = None


# Helper functions


def terminate(message):
    print(message)
    sys.exit()


# Client

def request_put(item):
    msg = pb2.PutReq(item=item)
    try:
        response = stub.put(msg, timeout=SERVER_RESPONSE_TIMEOUT)
    except grpc.RpcError:
        terminate("Server response timeout exceeded.")

    print(response.result)


def request_peek():
    msg = pb2.EmptyReq()
    try:
        response = stub.peek(msg, timeout=SERVER_RESPONSE_TIMEOUT)
    except grpc.RpcError:
        terminate("Server response timeout exceeded.")

    item = response.item
    if item == '':
        print('None')
    else:
        print(item)


def request_pop():
    msg = pb2.EmptyReq()
    try:
        response = stub.pop(msg, timeout=SERVER_RESPONSE_TIMEOUT)
    except grpc.RpcError:
        terminate("Server response timeout exceeded.")

    item = response.item
    if item == '':
        print('None')
    else:
        print(item)


def request_size():
    msg = pb2.EmptyReq()
    try:
        response = stub.size(msg, timeout=SERVER_RESPONSE_TIMEOUT)
    except grpc.RpcError:
        terminate("Server response timeout exceeded.")

    print(response.size)


def start_client():
    global channel
    global stub

    channel = grpc.insecure_channel(f"{HOST}:{PORT}")
    stub = pb2_grpc.QueueServiceStub(channel)

    while True:
        try:
            input_text = input('> ')
            command = input_text.split(" ")[0]

            if command == "put":
                try:
                    argument = input_text.split(" ")[1]
                except:
                    print("Unknown command")
                    continue

                request_put(argument)
            elif command == "peek":
                request_peek()
            elif command == "pop":
                request_pop()
            elif command == "size":
                request_size()
            else:
                print("Unknown command")
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