FROM ubuntu:latest

RUN apt-get update -y && apt-get install -y python3 pip python3-venv
RUN python3 -m venv venv
RUN python3 -m pip install flask flask_socketio waitress 

RUN mkdir /app
RUN mkdir /app/history
RUN mkdir /app/web
RUN mkdir /app/src
RUN mkdir /app/data
RUN mkdir /app/static

COPY py_app/server.py /app
COPY py_app/src/*.py /app

EXPOSE 5001

WORKDIR /app

# ENTRYPOINT ["/venv/bin/python3", "server.py"]
ENTRYPOINT ["waitress-serve", "--host", "0.0.0.0", "--call", "server:app"]
