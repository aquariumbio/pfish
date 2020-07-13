FROM sd2e/python3 as pfish-base

# install dependencies
RUN pip3 install --upgrade \
    cliff \
    pydent
 
# create directories within container
# /script is where the package lives
# /script/config is a mount point for users .pfish directory
RUN mkdir /script \
    mkdir -p /script/config
WORKDIR /script

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