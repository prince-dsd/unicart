# Step 1: Use an official Python runtime as a parent image
FROM python:3.9-slim

# Step 2: Set environment variables
ENV PYTHONUNBUFFERED 1

# Step 3: Set the working directory inside the container
WORKDIR /app

# Step 4: Install system dependencies (e.g., for building certain libraries like psycopg2)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Step 5: Copy the current directory contents into the container at /app
COPY . /app/

# Step 6: Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Step 7: Collect static files (if any)
RUN python manage.py collectstatic --noinput

# Step 8: Expose port (Uvicorn typically runs on port 8000)
EXPOSE 8000

# Step 9: Run Uvicorn server as the entrypoint
CMD ["uvicorn", "myproject.asgi:application", "--host", "0.0.0.0", "--port", "8000"]
