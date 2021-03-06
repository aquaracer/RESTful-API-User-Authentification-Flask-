FROM python:3.6-slim

RUN apt-get update

WORKDIR /usr/src

COPY  . /usr/src

RUN pip install -r requirements.txt

RUN chmod +x ./entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
