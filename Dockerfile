FROM python:latest

WORKDIR /HiveBox
COPY . .

CMD [ "python", "main.py" ]