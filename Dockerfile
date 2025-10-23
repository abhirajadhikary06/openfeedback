FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Pass token as environment variable
ARG LOGO_DEV_TOKEN
ENV LOGO_DEV_TOKEN=$LOGO_DEV_TOKEN

EXPOSE 5000

CMD ["python", "app.py"]