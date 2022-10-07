# Start from the fredericklab base container
FROM fredericklab/basecontainer:latest

# Installing precomputed python packages
RUN pip install \
                 statsmodels \
                 scikit-image \
                 scikit-learn \
                 pandas \
                 numba 
RUN pip install \
                 nilearn \
                 nibabel \
                 h5py
RUN pip install \
                 keras \
                 tensorflow
RUN pip install \
                 pyqt5
RUN pip install \
                 pyqtgraph 
RUN pip install \
                 versioneer \
                 tqdm \
                 pyfftw


# Create a shared $HOME directory
RUN useradd -m -s /bin/bash -G users rapidtide
WORKDIR /home/rapidtide
ENV HOME="/home/rapidtide"


# Installing rapidtide
COPY . /src/rapidtide
RUN cd /src/rapidtide && \
    python3 setup.py install && \
    rm -rf /src/rapidtide/build /src/rapidtide/dist


ENV IS_DOCKER_8395080871=1
RUN apt-get install -y --reinstall libxcb-xinerama0
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*


RUN ldconfig
WORKDIR /tmp/
ENTRYPOINT ["/usr/local/bin/rapidtide_dispatcher"]

# set a non-root user
#USER rapidtide

ARG VERSION
ARG BUILD_DATE
ARG VCS_REF

RUN echo $VERSION
RUN echo $BUILD_DATE
RUN echo $VCS_REF

LABEL org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.name="rapidtide" \
      org.label-schema.description="rapidtide - a set of tools for delay processing" \
      org.label-schema.url="http://nirs-fmri.net" \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.vcs-url="https://github.com/bbfrederick/rapidtide" \
      org.label-schema.version=$VERSION
