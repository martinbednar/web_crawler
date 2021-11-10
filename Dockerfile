FROM krallin/ubuntu-tini:bionic

SHELL ["/bin/bash", "-c"]

ENV browsers=--browsers=3
ENV sites=--sites=./oupensource_sites_to_be_visited.json
ENV start=--start=0
ENV offset=--offset=5513
ENV privacy=--privacy

# Update ubuntu and setup conda
# adapted from: https://hub.docker.com/r/conda/miniconda3/dockerfile
RUN sed -i'' 's/archive\.ubuntu\.com/us\.archive\.ubuntu\.com/' /etc/apt/sources.list
RUN apt-get clean -qq \
    && rm -r /var/lib/apt/lists/* -vf \
    && apt-get clean -qq \
    && apt-get update -qq \
    && apt-get upgrade -qq \
    # git and make for `npm install`, wget for `install-miniconda`
    && apt-get install wget git make -qq \
    # deps to run firefox inc. with xvfb
    && apt-get install libgtk-3-0 libx11-xcb1 libdbus-glib-1-2 libxt6 xvfb -qq

ENV HOME /opt
COPY scripts/install-miniconda.sh .
RUN ./install-miniconda.sh
ENV PATH $HOME/miniconda/bin:$PATH

# Install OpenWPM
WORKDIR /opt/OpenWPM
COPY . .
RUN ./install.sh
ENV PATH $HOME/miniconda/envs/openwpm/bin:$PATH

# Move the firefox binary away from the /opt/OpenWPM root so that it is available if
# we mount a local source code directory as /opt/OpenWPM
RUN mv firefox-bin /opt/firefox-bin
ENV FIREFOX_BINARY /opt/firefox-bin/firefox-bin

# Setting crawl-javascript-apis.py as the default command
# Pass arguments through docker run. Example:
# docker build -t web_crawler .
# docker run web_crawler --browsers=1 --sites=./sites_to_be_visited.json --start=0 --offset=1
CMD python crawl-javascript-apis.py ${browsers} ${sites} ${start} ${offset}
#ENTRYPOINT python crawl-javascript-apis.py ${browsers} ${sites} ${start} ${offset}

