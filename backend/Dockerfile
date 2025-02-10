FROM python:3.10.9-slim
RUN apt update && apt install -y libgl1-mesa-glx

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY http_server.py /app/
COPY image_processing.py /app/
COPY search.py /app/

CMD ["python", "http_server.py"]