FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        openssh-client \
        tcpdump \
        iputils-ping \
        netcat-openbsd \
        iproute2 \
        iptables \
        dsniff \
        procps && \
    rm -rf /var/lib/apt/lists/*

COPY knock_client.py ./
COPY demo.sh ./

# Make demo.sh executable
RUN chmod +x demo.sh

# Enable IP forwarding on container start
CMD ["sh", "-c", "sysctl -w net.ipv4.ip_forward=1 && tail -f /dev/null"]
