# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Disable Poetry's virtual environment creation
ENV POETRY_VIRTUALENVS_CREATE=false  

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies (e.g., for building certain libraries like psycopg2)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

# Copy the project files into the container
COPY . /app/

# Install dependencies using Poetry
RUN poetry install --no-root

# Collect static files (if any)
RUN python manage.py collectstatic --noinput

# Expose port (Uvicorn typically runs on port 8000)
EXPOSE 8000

# Run Uvicorn server as the entrypoint
CMD ["uvicorn", "unicart.asgi:application", "--host", "0.0.0.0", "--port", "8000"]
