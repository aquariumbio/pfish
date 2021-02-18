FROM python:3.9 as pfish-base

# create directories within container
# /script is where the package lives
ENV SCRIPT_DIR=/script
# /script/config is a mount point for users .pfish directory
RUN mkdir -p ${SCRIPT_DIR}/config
WORKDIR ${SCRIPT_DIR}

# install dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# copy script into container
COPY ./pxfish .

# create a working directory to be mounted as user working directory
RUN mkdir /wd
WORKDIR /wd

# run script by default
ENTRYPOINT [ "python3", "/script/pyfish.py"]

# NOTE: to run a shell in the container, you have to override the entrypoint
# at the command line:
#
# docker run -it --entrypoint /bin/bash aquariumbio/pfish
#