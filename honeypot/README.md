## Honeypot Design (SSH-themed)

An SSH-flavored honeypot listening on port 22 (exposed as 2222 via docker-compose). It mimics an Ubuntu 20.04 OpenSSH server, captures authentication attempts, and provides a faux shell with canned command outputs to keep adversaries engaged.

### Features
- Realistic banner: `SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.5` and login messaging (last login, MOTD).
- Captures and logs: source IP/port, timestamps, session duration, auth attempts (usernames/passwords), and every command with ordinal.
- Suspicious-activity alerts: repeated failed logins per IP and commands containing known attack keywords (wget, curl, nc, bash -i, etc.).
- Rotating text log plus structured JSONL event log for easy parsing.

### File Map
- `honeypot.py` — main server (thread-per-connection), fake shell, alerting.
- `logger.py` — shared logger and JSONL writer.
- `Dockerfile` — container build; mounts `./logs` for host-visible output.
- `logs/` — output directory (kept empty in repo; populated at runtime).
- `analysis.md` — place to summarize observed activity.

### Running
From repo root:

```bash
docker-compose up honeypot
# In another shell, interact locally:
ssh -p 2222 root@localhost
```

### What to Look For
- `logs/honeypot.log` — human-readable activity with INFO lines.
- `logs/connections.jsonl` — structured events (`connection`, `auth_attempt`, `auth_success`, `command`, `alert`, `session_summary`).

### Extending
- Add more canned command outputs in `COMMAND_RESPONSES` to deepen realism.
- Tweak `SUSPICIOUS_KEYWORDS` for your environment; forward `alert` events to a SIEM if desired.

### Attack simulation ideas
- Brute-force style auth: `ssh admin@localhost -p 2222` and try multiple passwords; watch `[LOGIN]` entries in [honeypot/logs/honeypot.log](honeypot/logs/honeypot.log).
- Credential reuse: attempt the advertised creds from the banner `ssh sshuser@localhost -p 2222` with `SecurePass2024!` to confirm session logging.
- Command probing: run `uname -a`, `id`, `ls /`, and injection-like payloads (`; curl http://evil`, `$(whoami)`) to see `[COMMAND]` captures and fake responses.
- Exit behavior: send `exit` or `quit` to observe disconnect handling in logs.
- Parallel connections: open multiple SSH sessions concurrently to test thread-per-connection handling and ensure all are logged.
