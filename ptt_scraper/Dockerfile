FROM python:3.8-alpine
WORKDIR /usr/src/ptt_project

COPY requirements.txt .
RUN apk update && apk add python3-dev \
                            gcc \
                            libc-dev \
                            libffi-dev
RUN pip install -r requirements.txt
COPY . /usr/src/ptt_project