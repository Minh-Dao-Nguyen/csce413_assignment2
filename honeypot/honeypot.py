#!/usr/bin/env python3
"""Simple SSH-themed honeypot implementation."""

import socket
import threading
import paramiko
import logging
import os
import time
from pathlib import Path
import textwrap

LOG_PATH = "/app/logs/honeypot.log"
HOST = "0.0.0.0"
PORT = 2222

HOST_KEY = paramiko.RSAKey.generate(2048)
BANNER = textwrap.dedent(
    """
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║          🔒 SECRET SSH SERVER 🔒                      ║
    ║                                                       ║
    ║  You have discovered a hidden service!                ║
    ║  Congratulations on your reconnaissance skills.       ║
    ║                                                       ║
    ║  Service: SSH Server                                  ║
    ║  Port: 2222                                           ║
    ║                                                       ║                          
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    """
)

COMMAND_RESPONSES = {
    "uname -a": "Linux ip-10-0-0-5 5.4.0-110-generic #124-Ubuntu SMP x86_64 GNU/Linux\n",
    "id": "uid=0(root) gid=0(root) groups=0(root)\n",
    "pwd": "/root\n",
    "ls": "bin  boot  etc  home  lib  lib64  tmp  var\n",
    "cat /etc/passwd": "root:x:0:0:root:/root:/bin/bash\nsshd:x:110:65534::/run/sshd:/usr/sbin/nologin\n",
}

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

    def get_banner(self):
        return BANNER + "\n", "en-US"

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
            "get_banner": get_banner,
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

        #channel.send("\n" + BANNER + "\r\n")
        channel.send("SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.5\r\n")
        channel.send("Ubuntu 20.04 LTS\r\n")
        channel.send("Last login: " + time.ctime() + "\r\n")
        channel.send("$ ")

        while True:
            command = ""
            while not (command.endswith("\r") or command.endswith("\n")):
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

            if command in COMMAND_RESPONSES:
                channel.send(COMMAND_RESPONSES[command])
            elif command.startswith("curl ") or command.startswith("wget "):
                channel.send("<html><body><h1>403 Forbidden</h1></body></html>\n")
            else:
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
