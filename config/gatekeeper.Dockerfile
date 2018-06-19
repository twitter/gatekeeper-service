FROM node:9-stretch

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

# Install bower
RUN npm i -g bower

# Change directory to install bower packages
RUN cd gate-keeping-service/static && bower install --allow-root

# Install packages needed for linux
RUN apt-get update && apt-get install -y apt-utils python2.7 python-dev python-pip build-essential libldap2-dev libssl-dev libsasl2-dev vim openjdk-8-jdk

# Need JDK/JRE

# Install packages from requirements.txt
RUN pip install --upgrade pip
RUN pip install -r gate-keeping-service/3rdparty/python/requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME World

# Create pex
RUN gate-keeping-service/pants binary :gatekeeper

# Run gatekeeper.pex when the container launches
CMD ["python", "gate-keeping-service/dist/gatekeeper.pex"]
