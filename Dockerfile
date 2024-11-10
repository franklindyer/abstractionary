FROM ubuntu:latest

RUN apt-get update -y && apt-get install -y python3 pip
RUN python3 -m pip install flask flask_socketio gensim

RUN mkdir /app
RUN mkdir /app/history
RUN mkdir /app/web
RUN mkdir /app/src
RUN mkdir /app/data

COPY server.py /app/server.py
COPY src/*.py /app/src/

EXPOSE 5001

WORKDIR /app

ENTRYPOINT ["python3", "server.py"]
