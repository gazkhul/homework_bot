FROM python:3.8-alpine
RUN mkdir /app
ADD . /app
WORKDIR /app
RUN apk update && apk add python3-dev gcc libc-dev
RUN pip install --upgrade pip --no-cache-dir
RUN pip install -r /app/requirements.txt --no-cache-dir
CMD [ "python", "homework.py" ]