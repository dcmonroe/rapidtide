# Start from the fredericklab base container
FROM fredericklab/basecontainer:latest

# get build arguments
ARG BUILD_TIME
ARG BRANCH
ARG GITVERSION
ARG GITSHA
ARG GITDATE

# set and echo environment variables
ENV BUILD_TIME=$BUILD_TIME
ENV BRANCH=$BRANCH
ENV GITVERSION=${GITVERSION}
ENV GITSHA=${GITSHA}
ENV GITDATE=${GITDATE}

RUN echo "BRANCH: "$BRANCH
RUN echo "BUILD_TIME: "$BUILD_TIME
RUN echo "GITVERSION: "$GITVERSION
RUN echo "GITSHA: "$GITSHA
RUN echo "GITDATE: "$GITDATE

# Copy rapidtide into container
COPY . /src/rapidtide
RUN ln -s /src/rapidtide/cloud /
RUN echo $GITVERSION > /src/rapidtide/VERSION

# init and install rapidtide
RUN uv pip install --upgrade pip
RUN cd /src/rapidtide && \
    uv pip install .
RUN chmod -R a+r /src/rapidtide

# install versioneer
RUN cd /src/rapidtide && \
    versioneer install --no-vendor && \
    rm -rf /src/rapidtide/build /src/rapidtide/dist

# install test data
#RUN cd /src/rapidtide/rapidtide/data/examples/src && \
#    ./installtestdatadocker

# update the paths to libraries
RUN ldconfig

# clean up
RUN pip cache purge

# switch to the rapidtide user
RUN useradd -m -s /bin/bash -G users rapidtide
RUN chown -R rapidtide /src/rapidtide
WORKDIR /home/rapidtide
ENV HOME="/home/rapidtide"
RUN /opt/miniforge3/bin/mamba init
RUN echo "mamba activate science" >> /home/rapidtide/.bashrc
RUN echo "/opt/miniforge3/bin/mamba activate science" >> /home/rapidtide/.bashrc
USER rapidtide

ENV BASH_ENV="/home/rapidtide/.bashrc"

ENV IS_DOCKER_8395080871=1

WORKDIR /tmp/
ENTRYPOINT ["/cloud/mount-and-run"]

LABEL org.label-schema.build-date=$BUILD_TIME \
      org.label-schema.name="rapidtide" \
      org.label-schema.description="rapidtide - a set of tools for delay processing" \
      org.label-schema.url="http://nirs-fmri.net" \
      org.label-schema.vcs-ref=$GITVERSION \
      org.label-schema.vcs-url="https://github.com/bbfrederick/rapidtide" \
      org.label-schema.version=$GITVERSION
