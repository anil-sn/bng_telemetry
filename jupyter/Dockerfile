# Start from a base Jupyter Notebook image that includes Python and common data science tools
FROM jupyter/scipy-notebook:latest

# Set the working directory for the user 'jovyan' which is the default in these images
WORKDIR /home/jovyan/work

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies using pip
# We switch to the root user to install packages globally, then switch back
USER root
RUN pip install --no-cache-dir -r requirements.txt
USER ${NB_UID}

# The base image already has a CMD to start Jupyter Lab, so we don't need to add one.
# Any notebooks will be placed in the '/home/jovyan/work' directory, which we map as a volume.