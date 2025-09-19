FROM ubuntu:22.04 AS builder
RUN apt-get update && apt-get install -y build-essential
WORKDIR /ubuntu-folder

FROM python:3.12-slim AS starter
WORKDIR /ubuntu-folder/app
COPY --from=builder /ubuntu-folder /ubuntu-folder/
COPY requirements.txt /ubuntu-folder/app/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /ubuntu-folder/app/
CMD ["python", "main.py"]