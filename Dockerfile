FROM debian:buster-slim
ENV LC_ALL=C.UTF-8
RUN apt update && apt upgrade -y && \
    apt-get install -y python3-pip && \ 
    useradd -m worker
USER worker
RUN mkdir /home/worker/src
WORKDIR /home/worker/src
RUN mkdir data && \
    mkdir log && \
    chown -R worker:worker /home/worker/src

COPY requirements.txt .
RUN pip3 install -r requirements.txt && \
    rm -f requirements.txt

COPY --chown=worker:worker koski-reader/reader.py .