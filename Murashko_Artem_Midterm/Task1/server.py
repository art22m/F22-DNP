import queue_pb2 as pb2
import queue_pb2_grpc as pb2_grpc

import grpc
import signal
import sys

from queue import Queue
from concurrent import futures

# Config

HOST = '127.0.0.1'
PORT = '5555'

MAX_QUEUE_SIZE = 10
MAX_WORKERS = 10

server_queue = Queue()


# Helper functions


def terminate(message):
    print(message)
    sys.exit()

# Server


class QueueServiceHandler(pb2_grpc.QueueServiceServicer):

    def put(self, request, context):
        item = request.item

        try:
            server_queue.put_nowait(item)
        except:
            return pb2.PutRep(result=False)

        return pb2.PutRep(result=True)

    def peek(self, request, context):
        try:
            item = server_queue.queue[0]
        except:
            return pb2.SimpleRep(item='')

        return pb2.SimpleRep(item=item)

    def pop(self, request, context):
        try:
            item = server_queue.get_nowait()
        except:
            return pb2.SimpleRep(item='')

        return pb2.SimpleRep(item=item)

    def size(self, request, context):
        queue_size = server_queue.qsize()
        return pb2.SizeRep(size=queue_size)


# Server functions


def start_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=MAX_WORKERS))
    pb2_grpc.add_QueueServiceServicer_to_server(QueueServiceHandler(), server)
    server.add_insecure_port(f"{HOST}:{PORT}")
    server.start()

    try:
        server.wait_for_termination()
    except KeyboardInterrupt as keys:
        terminate(f'{keys} was pressed, terminating server')


# Parsing


def parse_arguments():
    if len(sys.argv) != 3:
        terminate("Specify arguments in the following order: \n \
                  python3 server.py PORT QUEUE_SIZE")

    global PORT
    PORT = int(sys.argv[1])

    global MAX_QUEUE_SIZE
    MAX_QUEUE_SIZE = int(sys.argv[2])

    global server_queue
    server_queue = Queue(maxsize=MAX_QUEUE_SIZE)


# Main

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.default_int_handler)

    parse_arguments()

    try:
        start_server()
    except KeyboardInterrupt as keys:
        terminate(f'{keys} was pressed, terminating server')
