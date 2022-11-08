import queue
from multiprocessing import Queue
from threading import Thread
from multiprocessing import Lock

import socket
import sys
import signal

# Constants

HOST = '127.0.0.1'

BUFFER_SIZE = 1024

MAX_CLIENTS_NUMBER = 5
WORKER_THREADS_NUMBER = 3

# Config

clients = {} # [name : sock]
mutex = Lock()


server_port = 12300
tcp_socket = None


# Helper functions

def terminate(message):
    print(message)
    sys.exit()

# Server functions


def broadcast_to_clients():
    global clients

    names_list = list(clients.keys())
    names_list.sort()
    message = ' '.join(names_list) + '\n'

    for connection in clients.values():
        try:
            connection.sendall(message.encode())
        except:
            continue

# TCP Socket configuration


def create_tcp_socket():
    global tcp_socket

    try:
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.bind((HOST, server_port))
        tcp_socket.listen(5)
    except socket.error as error:
        terminate(f"Socket creation error {error}")

    print("Socket created")


def handle_connections(que):
    while True:
        try:
            connection, addr = tcp_socket.accept()
            distribute_connection(connection, addr, que)
        except KeyboardInterrupt as keys:
            tcp_socket.close()
            terminate(f'{keys} was pressed, terminating server')


def distribute_connection(connection, addr, que):
    try:
        que.put_nowait((connection, addr))
        print(f"Connection {addr[1]} added to the processing queue")
    except queue.Full:
        message = "Maximum number of connections, try again later"
        connection.sendall(message.encode())
        connection.close()
    except:
        return

# Worker functions


def handle_client(connection, addr):
    global clients
    global mutex

    try:
        data = connection.recv(BUFFER_SIZE)
        if not data:
            connection.close()
            terminate(f"{addr[1]} closed the connection")
    except:
        connection.close()
        terminate(f"{addr[1]} closed the connection")

    name = data.decode()
    with mutex:
        clients[name] = connection

    broadcast_to_clients()

    while True:
        data = connection.recv(BUFFER_SIZE)

        if not data:
            with mutex:
                clients.pop(name)

            connection.close()
            broadcast_to_clients()
            terminate(f"{addr[1]} closed the connection")

        continue


def start_worker(que):
    while True:
        try:
            connection, addr = que.get()
            print(f"Worker took the connection {addr[1]} for processing")
            handle_client(connection, addr)
        except:
            continue


def create_workers(que):
    for _ in range(WORKER_THREADS_NUMBER):
        worker_thread = Thread(target=start_worker, args=(que,), daemon=True)
        worker_thread.start()


# Parsing


def parse_arguments():
    if len(sys.argv) != 2:
        terminate("Specify arguments in the following order: \n \
                  python3 server.py port")

    global server_port
    server_port = int(sys.argv[1])


# Main

def start_server():
    create_tcp_socket()
    que = Queue(MAX_CLIENTS_NUMBER)
    create_workers(que)
    handle_connections(que)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.default_int_handler)

    parse_arguments()

    try:
        start_server()
    except KeyboardInterrupt as keys:
        terminate(f'{keys} was pressed, terminating server')