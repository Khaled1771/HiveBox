FROM python:3.12-slim

WORKDIR /HiveBox
COPY . .

CMD [ "python", "main.py" ]