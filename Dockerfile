# Base image
FROM python:3.10-slim

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Working directory inside container
WORKDIR /usr/src/app

# Required system packages
RUN apt-get update && apt-get install -y \
    build-essential libpq-dev netcat-traditional && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY auth_system/requirements.txt ./requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the entire project (important for users + ticket apps)
COPY . /usr/src/app/

# Copy entrypoint
RUN chmod +x /usr/src/app/entrypoint.sh

# Add project root to Python import path
ENV PYTHONPATH="/usr/src/app"

CMD ["/usr/src/app/entrypoint.sh"]
