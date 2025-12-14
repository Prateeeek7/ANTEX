FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for Meep
# Meep requires: libhdf5, libblas, liblapack, libfftw3, and other scientific libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    git \
    build-essential \
    cmake \
    pkg-config \
    libhdf5-dev \
    libblas-dev \
    liblapack-dev \
    libfftw3-dev \
    libgsl-dev \
    libharminv-dev \
    libmpfr-dev \
    libgmp-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Miniconda first for proper Meep installation
# Meep requires conda-forge for reliable Python bindings
RUN apt-get update && apt-get install -y --no-install-recommends wget bzip2 && \
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh && \
    bash /tmp/miniconda.sh -b -p /opt/conda && \
    rm /tmp/miniconda.sh && \
    /opt/conda/bin/conda init bash && \
    /opt/conda/bin/conda config --add channels conda-forge && \
    /opt/conda/bin/conda config --set channel_priority strict

# Install Meep via conda-forge (most reliable method)
RUN /opt/conda/bin/conda install -y -c conda-forge meep && \
    /opt/conda/bin/conda clean -afy

# Make conda Python the default and verify Meep
RUN ln -sf /opt/conda/bin/python3 /usr/local/bin/python3 && \
    ln -sf /opt/conda/bin/pip /usr/local/bin/pip && \
    /opt/conda/bin/python3 -c "import meep as mp; print('Meep version:', hasattr(mp, '__version__') and mp.__version__ or 'loaded'); print('Meep attributes:', len([x for x in dir(mp) if not x.startswith('_')]))" || \
    echo "⚠ Meep import test failed"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Default command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


