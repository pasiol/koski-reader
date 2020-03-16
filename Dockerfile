FROM debian:buster-slim
ENV LC_ALL=C.UTF-8
RUN apt update && apt upgrade -y && \
    apt-get install -y python3-pip && \ 
    useradd -m worker
USER worker
RUN mkdir /home/worker/src
WORKDIR /home/worker/src
RUN chown -R worker:worker /home/worker/src && \
    mkdir data && \
    chown -R worker:worker data && \
    mkdir log && \
    chown -R worker:worker log

COPY requirements.txt .
RUN pip3 install -r requirements.txt && \
    rm -f requirements.txt

COPY --chown=worker:worker reader.py .
ENTRYPOINT ["python3", "reader.py"]