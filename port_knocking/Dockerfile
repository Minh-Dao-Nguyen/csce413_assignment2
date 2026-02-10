# FROM python:3.11-slim

# WORKDIR /app

# RUN apt-get update \
#     && apt-get install -y --no-install-recommends iptables iproute2 \
#     && rm -rf /var/lib/apt/lists/*

# COPY knock_server.py knock_client.py ./

# CMD ["python3", "knock_server.py"]

# # /sbin/iptables -A INPUT -p tcp --dport 22 -j DROP & knockd 

FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    openssh-server \
    knockd \
    iptables \
    net-tools \
    python3 \
    tcpdump \
    && rm -rf /var/lib/apt/lists/*

# Create ssh directory
RUN mkdir /var/run/sshd

# Create user for SSH login
RUN useradd -m user && echo "user:user" | chpasswd

# Configure SSH to use port 2222
# RUN sed -i 's/#Port 22/Port 2222/' /etc/ssh/sshd_config && \
#     sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config && \
#     sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config

RUN sed -i 's/#Port 22/Port 2222/' /etc/ssh/sshd_config && \
    sed -i 's/#ListenAddress 0.0.0.0/ListenAddress 0.0.0.0/' /etc/ssh/sshd_config

# Copy knockd config
COPY knockd.conf /etc/knockd.conf

# Enable knockd
RUN sed -i 's/START_KNOCKD=0/START_KNOCKD=1/' /etc/default/knockd

# Copy startup script
COPY start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 2222

CMD ["/start.sh"]


