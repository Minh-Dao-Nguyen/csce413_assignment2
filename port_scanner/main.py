#!/usr/bin/env python3
"""
Port Scanner - Starter Template for Students
Assignment 2: Network Security

This is a STARTER TEMPLATE to help you get started.
You should expand and improve upon this basic implementation.

TODO for students:
1. Implement multi-threading for faster scans
2. Add banner grabbing to detect services
3. Add support for CIDR notation (e.g., 192.168.1.0/24)
4. Add different scan types (SYN scan, UDP scan, etc.)
5. Add output formatting (JSON, CSV, etc.)
6. Implement timeout and error handling
7. Add progress indicators
8. Add service fingerprinting
"""

import argparse
import ipaddress
import socket
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed


def scan_port(target, port, timeout=3.0):
    """
    Scan a single port on the target host

    Args:
        target (str): IP address or hostname to scan
        port (int): Port number to scan
        timeout (float): Connection timeout in seconds

    Returns:
        bool: True if port is open, False otherwise
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((target, port))
        sock.close()
        return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False
    # try:
    #     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    #         sock.settimeout(timeout)
    #         if port == 2222:
    #             print(f"[*] Scanning port {port} on {target}...")
    #             print("res:", sock.connect_ex((target, port)))
    #         return sock.connect_ex((target, port)) == 0
    #     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     sock.settimeout(timeout)
    #     # connect_ex returns 0 on success, errno otherwise
    #     #print(f"[*] Scanning port {port} on {target}...")
    #     res = sock.connect_ex((target, port))
    #     #print(f"[*] Finished scanning port {port} on {target}: result={res}")
    #     sock.close()
    #     return res == 0
    # except (socket.timeout, ConnectionRefusedError, OSError):
    #     return False


def scan_range(target, start_port, end_port, threads, timeout):
    """
    Scan a range of ports on the target host

    Args:
        target (str): IP address or hostname to scan
        start_port (int): Starting port number
        end_port (int): Ending port number

    Returns:
        list: List of open ports
    """
    open_ports = []

    print(f"[*] Scanning {target} from port {start_port} to {end_port} with {threads} threads")
    #print(f"[*] This may take a while...")

    # TODO: Implement the scanning logic
    # Hint: Loop through port range and call scan_port()
    # Hint: Consider using threading for better performance

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {
            executor.submit(scan_port, target, port, timeout): port
            for port in range(start_port, end_port + 1)
        }

        for future in as_completed(futures):
            port = futures[future]
            if future.result():
                open_ports.append(port)
                print(f"[+] Port {port} is open")


        # for port in range(start_port, end_port + 1):
        #     # TODO: Scan this port
        #     scan = scan_port(target, port)
        #     # TODO: If open, add to open_ports list
        #     if scan:
        #         open_ports.append(port)
        #     # TODO: Print progress (optional)
        #     print(f"[*] Scanned port {port}")

    return open_ports


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Simple Port Scanner")
    parser.add_argument("--target", required=True, help="IP address/hostname or CIDR, e.g. 192.168.1.0/24")
    parser.add_argument("--ports", required=True, help="Port range in start-end format, e.g. 1-1024")
    parser.add_argument("--threads", type=int, default=100, help="Number of worker threads")
    parser.add_argument("--timeout", type=float, default=1.0, help="Per-connection timeout in seconds")
    args = parser.parse_args()

    start_port, end_port = map(int, args.ports.split("-"))

    if start_port < 1 or end_port > 65535 or start_port > end_port:
        print("[!] Port range must be between 1 and 65535 and start <= end")
        sys.exit(1)

    targets = []
    try:
        net = ipaddress.ip_network(args.target, strict=False)
        #print("Ips:", list(net.hosts()))
        targets = [str(ip) for ip in net.hosts() if str(ip) != "172.20.0.1"]
        #print("Targets:", targets)
        # targets = ["172.20.0.20", "172.20.0.22", "172.20.0.11", "172.20.0.10", "172.20.0.21"]
    except ValueError:
        targets = [args.target]

    all_results = {}
    for target in targets:
        print(f"\n[*] Starting scan for {target}")
        open_ports = scan_range(target, start_port, end_port, args.threads, args.timeout)
        all_results[target] = open_ports

    print(f"\n[+] Scan complete!")
    for target, open_ports in all_results.items():
        print(f"[+] {target}: found {len(open_ports)} open ports")
        for port in sorted(open_ports):
            print(f"    Port {port}: open")


if __name__ == "__main__":
    main()
