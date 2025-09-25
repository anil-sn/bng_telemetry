FROM jupyter/scipy-notebook:latest

USER root

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

USER $NB_UID

# Copy requirements and install Python packages
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy notebooks
COPY notebooks/ /home/jovyan/notebooks/

# Set working directory
WORKDIR /home/jovyan

# Start Jupyter Lab
CMD ["start.sh", "jupyter", "lab", "--LabApp.token=''", "--LabApp.password=''"]