FROM node:9-stretch as base

# Install packages needed on linux
RUN apt-get update && apt-get install -y \
apt-utils \
python2.7 \
python-dev \
python-pip \
build-essential \
libldap2-dev \
libssl-dev \
libsasl2-dev \
openjdk-8-jdk

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

# Install packages from requirements.txt
RUN pip install --upgrade pip
RUN pip install -r 3rdparty/python/requirements.txt

# Install bower
RUN npm i -g bower

# Change directory to install bower packages
RUN cd static && bower install --allow-root

# Make port 5000 available outside the container
EXPOSE 5000

# Create the pex file
RUN ./pants clean-all binary :gatekeeper

# Import python and remove base container
FROM python:2.7.14

# Set the working directory to /app
WORKDIR /app

# Copy project files
ADD . /app

# Copy pex from base build
COPY --from=base /app/dist /app/dist
COPY --from=base /app/static /app/static

# Run gatekeeper.pex when container starts
CMD ["python", "dist/gatekeeper.pex"]
