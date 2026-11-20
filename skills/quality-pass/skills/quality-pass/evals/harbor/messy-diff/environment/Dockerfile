FROM python:3.12-slim

RUN apt-get -o Acquire::Retries=3 update && \
    apt-get -o Acquire::Retries=3 install -y --no-install-recommends bash curl git jq procps ripgrep && \
    rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir pytest==8.3.5

RUN mkdir -p /workspace/skills /logs/agent /logs/verifier

# A committed baseline, then an uncommitted messy change on top of it.
COPY seed/base/ /workspace/project/
RUN cd /workspace/project && git init -q -b main && \
    git -c user.name=dev -c user.email=dev@example.com add -A && \
    git -c user.name=dev -c user.email=dev@example.com commit -qm "Add line_total"
COPY seed/change/orders.py /workspace/project/orders.py
WORKDIR /workspace/project
