"""
    Server
    Lab 02 Murashko Artem
"""

import queue
from multiprocessing import Queue
from threading import Thread

import socket
import sys
import signal

# Constants

HOST = '127.0.0.1'

BUFFER_SIZE = 1024

MAX_CLIENTS_NUMBER = 3
WORKER_THREADS_NUMBER = 3

# Config

server_port = 12300
tcp_socket = None


# Helper functions

def terminate(message):
    log(message)
    sys.exit()


def log(message):
    print(message)


# Server functions

# TCP Socket configuration

def create_tcp_socket():
    global tcp_socket

    try:
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.bind((HOST, server_port))
        tcp_socket.listen(5)
    except socket.error as error:
        terminate(f"Socket creation error {error}")

    log("Socket created")


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
        log(f"Connection {addr[1]} added to the processing queue")
    except queue.Full:
        message = "Maximum number of connections, try again later"
        connection.sendall(message.encode())
        connection.close()
    except:
        return


def handle_client(connection, addr):
    def is_prime(n):
        if n in (2, 3):
            return True
        if n % 2 == 0:
            return False
        for divisor in range(3, n, 2):
            if n % divisor == 0:
                return False
        return True

    while True:
        data = connection.recv(BUFFER_SIZE)

        if not data:
            break

        number = int(data.decode())
        answer = f"{number} is " + ("prime" if is_prime(number) else "not prime")
        connection.sendall(answer.encode())

    log(f"Work with connection {addr[1]} is done, closing...")
    connection.close()


# Worker functions


def start_worker(que):
    while True:
        try:
            connection, addr = que.get()
            log(f"Worker took the connection {addr[1]} for processing")
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
    start_server()
