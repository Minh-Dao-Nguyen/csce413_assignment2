#from .main import main
import socket

import argparse
import ipaddress
import socket
import sys
import threading
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

lock = threading.Lock()

def ping_target(target, timeout=1):
    try:
        print(f"Pinging {target}...")
        result = subprocess.run(["ping", "-c", "1", target],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL,
                                timeout=timeout)
        print(f"Finished pinging {target}: returncode={result.returncode}")
        return result.returncode == 0
    except Exception:
        return False


def scan_port(target, port, timeout=3.0):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((target, port))
        sock.close()
        return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


def scan_range(target, start_port, end_port, threads, timeout, results):
    open_ports = []

    print(f"Scanning {target} from port {start_port} to {end_port}")

    # with ThreadPoolExecutor(max_workers=threads) as executor:
    #     futures = {
    #         executor.submit(scan_port, target, port, timeout): port
    #         for port in range(start_port, end_port + 1)
    #     }

    #     for future in as_completed(futures):
    #         port = futures[future]
    #         if future.result():
    #             open_ports.append(port)
    #             print(f"[+] {target}: Port {port} is open")
    # results[target] = open_ports

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [executor.submit(scan_port, target, port, timeout) for port in range(start_port, end_port + 1)]
        for future in as_completed(futures):
            if future.result(): open_ports.append(futures.index(future) + start_port)
    with lock: results[target] = open_ports

def try_probe(target, port, payload=None, timeout=2):
    try:
        s = socket.socket()
        s.settimeout(timeout)
        s.connect((target, port))
        if payload:
            s.sendall(payload)
        data = s.recv(1024)
        s.close()
        return data.decode(errors="ignore").strip()
    except:
        return None


def detect_service(target, port, timeout=2):
    # Redis
    if port == 6379:
        banner = try_probe(target, port, b"*1\r\n$4\r\nPING\r\n", timeout)
        if banner: return "Redis: " + banner

    # MySQL (handshake banner on connect)
    if port == 3306:
        banner = try_probe(target, port, None, timeout)
        if banner: return "MySQL: " + banner

    # HTTP
    banner = try_probe(target, port, b"GET / HTTP/1.0\r\nHost: test\r\n\r\n", timeout)
    if banner: return "HTTP: " + banner

    # Generic banner (SSH, FTP, SMTP, etc.)
    banner = try_probe(target, port, b"\r\n", timeout)
    if banner: return "Generic: " + banner

    return None


def main():
    parser = argparse.ArgumentParser(description="Simple Port Scanner")
    parser.add_argument("--target", required=True, help="IP/hostname or CIDR")
    parser.add_argument("--ports", required=True, help="Port range (start-end)")
    parser.add_argument("--threads", type=int, default=100)
    parser.add_argument("--timeout", type=float, default=1.0)
    args = parser.parse_args()

    start_port, end_port = map(int, args.ports.split("-"))

    if start_port < 1 or end_port > 65535 or start_port > end_port:
        print("[!] Invalid port range")
        sys.exit(1)

    # Build target list
    try:
        net = ipaddress.ip_network(args.target, strict=False)
        targets = [str(ip) for ip in net.hosts()]
    except ValueError:
        targets = [args.target]

    # target_lst = ["172.20.0.20", "172.20.0.22", "172.20.0.11", "172.20.0.10", "172.20.0.21"]
    # for i in target_lst:
    #     print("in target list:", i, i in targets)

    alive_targets = []
    print("Pinging for ip lists")

    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = {executor.submit(ping_target, target): target for target in targets}
        for f in as_completed(futures):
            target = futures[f]
            if f.result():
                print("Found:", target)
                alive_targets.append(target)
        

    results = {}

    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = [executor.submit(scan_range, target, start_port, end_port, args.threads, args.timeout, results) for target in alive_targets]
        for f in as_completed(futures): f.result()

    for i, j in results.items():
        for port in sorted(j):
            print(f"{i}: Port {port} is open")

    print("check sevices")
    service_hosts = []  # final list of (target, port, service)

    for target, ports in results.items():
        for port in sorted(ports):
            service = detect_service(target, port)
            if service:
                service_hosts.append((target, port, service))
                print(f"{target}:{port} -> {service}")

    print('-'* 50)
    print("\nFinal list (targets with services):")
    for target, port, service in service_hosts:
        print(f"{target}:{port} -> {service}")


if __name__ == "__main__":
    main()
