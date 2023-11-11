FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip3 install --upgrade pip

RUN pip3 install -r ./requirements.txt --no-cache-dir

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:10000", "foodgram.wsgi"]
