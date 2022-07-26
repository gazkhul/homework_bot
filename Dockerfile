FROM python:3.8-alpine
RUN mkdir /app
ADD . /app
WORKDIR /app
RUN apk update && apk add python3-dev \
                        gcc \
                        libc-dev
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
CMD [ "python", "homework.py" ]