FROM python:3.11-slim

WORKDIR /port_scanner

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        iputils-ping \
        netcat-openbsd

COPY port_scanner port_scanner

ENTRYPOINT ["python3", "-m", "port_scanner"]
