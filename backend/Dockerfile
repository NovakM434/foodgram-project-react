FROM python:3.9

RUN pip install --upgrade pip --no-cache-dir

WORKDIR /app

COPY requirements.txt ./

RUN pip install -r /app/requirements.txt --no-cache-dir

COPY . .

CMD ["gunicorn", "foodgram.wsgi", "--bind", "0.0.0.0:8000"]