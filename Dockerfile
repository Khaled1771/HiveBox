FROM python:3.12-slim
# Install Curl
RUN apt update && apt install curl -y

WORKDIR /HiveBox
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 5000
CMD [ "python", "main.py" ]