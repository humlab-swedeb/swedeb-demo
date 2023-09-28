FROM ubuntu:20.04 as builder

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update -qq \
    && apt install -y -qq build-essential

RUN apt install -y -qq --no-install-recommends \
    apt-utils pkg-config sudo \
    autoconf bison flex subversion tar \
    libglib2.0-0 libglib2.0-dev \
    libncurses5 libncurses5-dev \
    libpcre3-dev \
    libreadline8 libreadline-dev \
    && rm -rf /var/lib/apt/lists/*

#####################################################################################
# Compile CWB Core
#####################################################################################

WORKDIR /usr/local/src

ADD https://svn.code.sf.net/p/cwb/code/cwb/trunk cwb.revision
RUN svn co -r HEAD --trust-server-cert --non-interactive --quiet https://svn.code.sf.net/p/cwb/code/cwb/trunk/ cwb

WORKDIR /usr/local/src/cwb

RUN touch local_config.mk \
    && echo "export PLATFORM=linux-native" >> local_config.mk \
    && install-scripts/install-linux


RUN svn co --trust-server-cert --non-interactive --quiet https://svn.code.sf.net/p/cwb/code/perl/trunk cwb-perl \
    && cd cwb-perl/CWB \
    && perl Makefile.PL --config=/usr/local/bin/cwb-config \
    && make \
    && make test \
    && make install


RUN cd /usr/local/bin && tar -cf /tmp/cwb.bin.install.tar cqp* cwb* \
    && cd /usr/local/include && tar -cf /tmp/cwb.include.install.tar cwb \
    && cd /usr/local/lib && tar -cf /tmp/cwb.lib.install.tar libcl*

#####################################################################################
# Final Image
#####################################################################################

FROM ubuntu:20.04

LABEL maintainer="Rebekka Weegar <rebecka dot weegar at umu dot se>"

# sudo addgroup -gid 1021 swedeb
# sudo adduser swedeb --uid 1021 --gid 1021 --disabled-password --gecos '' --shell /bin/bash

ARG SWEDEB_UID="1021"
ARG SWEDEB_GID="1021"
ARG SWEDEB_USER="swedeb"

ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive
ENV LD_LIBRARY_PATH=/usr/local/lib

RUN apt update -qq \
    && apt upgrade -y -qq > /dev/null \
    && apt install -y -qq --no-install-recommends \
        build-essential autoconf libtool pkg-config software-properties-common apt-utils \
    && apt update -qq \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt install -y -qq --no-install-recommends \
        perl curl python3.11 python3-pip python3.11-venv python3.11-dev \
        bison flex libglib2.0-0 readline-common libncurses5 libreadline8 \
        libglib2.0-dev \
        libncurses5-dev \
        libpcre3-dev \
        perl less gzip bzip2 make git sudo \
    && rm -rf /var/lib/apt/lists/*

RUN addgroup --gid $SWEDEB_GID "${SWEDEB_USER}"  \
  && adduser $SWEDEB_USER --uid $SWEDEB_UID --gid $SWEDEB_GID --disabled-password --gecos '' --shell /bin/bash \
  && adduser $SWEDEB_USER sudo \
  && echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

WORKDIR /usr/local
COPY --from=builder /tmp/cwb.bin.install.tar /tmp/cwb.bin.install.tar
COPY --from=builder /tmp/cwb.lib.install.tar /tmp/cwb.lib.install.tar
COPY --from=builder /tmp/cwb.include.install.tar /tmp/cwb.include.install.tar
RUN tar xf /tmp/cwb.bin.install.tar -C /usr/local/bin \
    && tar xf /tmp/cwb.lib.install.tar -C /usr/local/lib \
    && tar xf /tmp/cwb.include.install.tar -C /usr/local/include \
    && rm -f /tmp/cwb.*.install.tar

WORKDIR /data
WORKDIR /app

ENV HOME=/home/${SWEDEB_USER}
RUN chown -R ${SWEDEB_USER}:${SWEDEB_USER} /app /data

USER ${SWEDEB_USER}

ENV CORPUS_REGISTRY=/data/registry

RUN python3.11 -m venv ${HOME}/.venv \
   && . ${HOME}/.venv/bin/activate

ENV PATH="${HOME}/.venv/bin:$PATH"

RUN pip install swedeb-explorer
COPY app.py /app/app.py
COPY .env /app/.env

ARG SWEDEB_ENV_FILENAME=/app/.env
ARG SWEDEB_DEBUG=False
ARG SWEDEB_CWB_REGISTRY=/data/registry
ARG SWEDEB_CWB_DATABASE=RIKSPROT_V090_TEST

ENV SWEDEB_ENV_FILENAME=$SWEDEB_ENV_FILENAME
ENV SWEDEB_DEBUG=$SWEDEB_DEBUG
ENV SWEDEB_CWB_REGISTRY=$SWEDEB_CWB_REGISTRY
ENV SWEDEB_CWB_DATABASE=$SWEDEB_CWB_DATABASE

EXPOSE 8501
VOLUME /data
VOLUME /app

ENTRYPOINT ["streamlit", "run", "app.py",  "--server.port=8501", "--server.address=0.0.0.0"]
