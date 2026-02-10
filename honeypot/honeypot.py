#!/usr/bin/env python3
"""Simple SSH-themed honeypot implementation."""

import socket
import threading
import paramiko
import logging
import os
import time

LOG_PATH = "/app/logs/honeypot.log"
HOST = "0.0.0.0"
PORT = 2222

HOST_KEY = paramiko.RSAKey.generate(2048)


def setup_logging():
    os.makedirs("/app/logs", exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(LOG_PATH), logging.StreamHandler()],
    )


def create_server_interface(addr):
    def check_auth_password(self, username, password):
        logging.info(f"[LOGIN] {addr} | user={username} pass={password}")
        return paramiko.AUTH_SUCCESSFUL

    def get_allowed_auths(self, username):
        return "password"

    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_shell_request(self, channel):
        return True

    def check_channel_pty_request(self, *args, **kwargs):
        return True

    Server = type(
        "Server",
        (paramiko.ServerInterface,),
        {
            "check_auth_password": check_auth_password,
            "get_allowed_auths": get_allowed_auths,
            "check_channel_request": check_channel_request,
            "check_channel_shell_request": check_channel_shell_request,
            "check_channel_pty_request": check_channel_pty_request,
        },
    )

    return Server()


def handle_client(client, addr):
    logging.info(f"[CONNECT] {addr}")

    try:
        transport = paramiko.Transport(client)
        transport.add_server_key(HOST_KEY)

        server = create_server_interface(addr)
        transport.start_server(server=server)

        channel = transport.accept(20)
        if channel is None:
            logging.warning(f"[NO CHANNEL] {addr}")
            return

        channel.send("Ubuntu 20.04 LTS\n")
        channel.send("Last login: " + time.ctime() + "\n")
        channel.send("$ ")

        while True:
            command = ""
            while not command.endswith("\r"):
                data = channel.recv(1024).decode("utf-8")
                if not data:
                    break
                command += data

            command = command.strip()
            if not command:
                break

            logging.info(f"[COMMAND] {addr} | {command}")

            if command.lower() in ["exit", "quit"]:
                channel.send("logout\n")
                break

            channel.send(f"{command}: command not found\n")
            channel.send("$ ")

    except Exception as e:
        logging.error(f"[ERROR] {addr} | {e}")

    finally:
        client.close()
        logging.info(f"[DISCONNECT] {addr}")


def run_honeypot():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen(100)

    logging.info(f"SSH Honeypot running on {HOST}:{PORT}")

    while True:
        client, addr = sock.accept()
        threading.Thread(target=handle_client, args=(client, addr), daemon=True).start()


if __name__ == "__main__":
    setup_logging()
    run_honeypot()
