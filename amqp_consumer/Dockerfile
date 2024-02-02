# Stage 1: Build
FROM python:3.8-alpine as builder

WORKDIR /install

# Install compile dependencies
RUN apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev

# Install Python packages
COPY requirements.txt .
RUN pip install --prefix="/install" -r requirements.txt

# Stage 2: Runtime
FROM python:3.8-alpine

WORKDIR /app

# Install runtime dependencies
RUN apk add --no-cache libpq

# Copy installed Python packages from builder stage
COPY --from=builder /install /usr/local

# Copy the entire amqp_consumer module
COPY . /app/

CMD ["python", "main.py"]
