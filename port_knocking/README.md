## Port Knocking Starter Template

This directory is a starter template for the port knocking portion of the assignment.

### What you need to implement
- Pick a protected service/port (default is 2222).
- Define a knock sequence (e.g., 1234, 5678, 9012).
- Implement a server that listens for knocks and validates the sequence.
- Open the protected port only after a valid sequence.
- Add timing constraints and reset on incorrect sequences.
- Implement a client to send the knock sequence.

### Getting started
1. Implement your server logic in `knock_server.py`.
2. Implement your client logic in `knock_client.py`.
3. Update `demo.sh` to demonstrate your flow.
4. Run from the repo root with `docker compose up port_knocking`.

### Example usage
```bash
python3 knock_client.py --target 172.20.0.40 --sequence 1234,5678,9012
```

### Implementation overview
- Container builds from Ubuntu 22.04 with `openssh-server`, `knockd`, and `iptables`; SSH is moved to port 2222 and a demo user `user:user` is created in [port_knocking/Dockerfile](port_knocking/Dockerfile#L15-L54).
- Knockd is configured to open 2222 after the TCP SYN sequence `1234,5678,9012` and to close it with the reverse sequence in [port_knocking/knockd.conf](port_knocking/knockd.conf#L1-L15).
- Startup script [port_knocking/start.sh](port_knocking/start.sh#L1-L41) flushes rules, allows loopback and established traffic, drops 2222 by default, then runs `knockd` and `sshd` (knockd inserts/removes the ACCEPT rule for validated clients).
- Client [port_knocking/knock_client.py](port_knocking/knock_client.py#L1-L93) sends TCP connect_ex knocks with a default 0.3s delay; sequence, delay, protected port (2222), and post-knock connectivity check are CLI options.
- Demo script [port_knocking/demo.sh](port_knocking/demo.sh#L1-L17) probes 2222 with `nc`, runs the client, and probes again so you can see the port transition.
