FROM python:3.12-slim

WORKDIR /HiveBox
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 5000
CMD [ "pythonn", "main.py" ]
