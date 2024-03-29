FROM python:3.8-alpine
RUN mkdir /app
ADD . /app
WORKDIR /app
RUN apk update && apk add python3-dev gcc libc-dev
RUN python -m pip install --upgrade pip --no-cache-dir
RUN pip install -r requirements.txt --no-cache-dir
CMD [ "python", "homework.py" ]