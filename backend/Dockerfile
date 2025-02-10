FROM python:3.10.9
RUN apt-get update && apt-get install -y libgl1

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY .env /app/
COPY http_server.py /app/
COPY image_processing.py /app/
COPY search.py /app/

CMD ["python", "http_server.py"]