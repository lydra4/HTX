FROM python:3.12-slim

ARG DEBIAN_FRONTEND=noninteractive

# Update OS libraries to latest patched versions
# Update OS libraries
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

ARG DEBIAN_FRONTEND="noninteractive"

ARG NON_ROOT_USER="HTX"
ARG NON_ROOT_UID="2222"
ARG NON_ROOT_GID="2222"

# Create group and user
RUN groupadd -g ${NON_ROOT_GID} ${NON_ROOT_USER} && \
    useradd -m -s /bin/bash -u ${NON_ROOT_UID} -g ${NON_ROOT_GID} ${NON_ROOT_USER}

ENV PYTHONIOENCODING=utf8
ENV LC_ALL=C.utf8

WORKDIR /app

# Copy only the requirements file first to leverage Docker cache
COPY requirements-prod.txt .

# Install pip requirements as root into system site-packages so packages
# are available regardless of runtime mounts that may overlay the user's home.
RUN pip install --upgrade pip setuptools urllib3 && \
    pip install --no-cache-dir -r requirements-prod.txt

# Copy the rest of the application code and set correct ownership
COPY --chown=${NON_ROOT_USER}:${NON_ROOT_GID} . .

# Switch to the non-root user for running the application
USER ${NON_ROOT_USER}
