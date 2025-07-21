FROM python:3.12-slim
# Install Curl
RUN apt-get update && \
    apt-get install --no-install-recommends -y curl=8.5.0 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /HiveBox
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 5000
CMD [ "python", "main.py" ]