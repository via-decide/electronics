FROM debian:12.7@sha256:a590dc26218c6a51c912b1f7baf0fbd89cbb172de4a216b5cb308bda6ee29f23
RUN apt-get update && apt-get install -y --no-install-recommends build-essential=12.9 cmake=3.25.1-1 python3=3.11.2-1+b1 python3-pip=23.0.1+dfsg-1 git=1:2.39.5-0+deb12u2 ca-certificates=20230311 && rm -rf /var/lib/apt/lists/*
WORKDIR /workspace/electronics
COPY requirements.lock .
RUN pip3 install --break-system-packages --no-cache-dir -r requirements.lock
