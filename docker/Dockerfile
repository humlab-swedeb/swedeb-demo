FROM ubuntu:20.04 as builder

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update \
    && apt install -y build-essential

RUN apt install -y --no-install-recommends \
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
    && cd /usr/local/lib && tar -cf /tmp/cwb.lib.install.tar libcl*

# #####################################################################################
# # Final Image
# #####################################################################################

FROM python:3.11.5

LABEL maintainer="Rebekka Weegar <rebecka dot weegar at umu dot se>"

ARG SWEDEB_UID="201"
ARG SWEDEB_GID="2001"
ARG SWEDEB_USER="swedeb"

RUN addgroup --gid $SWEDEB_GID "${SWEDEB_USER}"  \
  && adduser $SWEDEB_USER --uid $SWEDEB_UID --gid $SWEDEB_GID --disabled-password --gecos '' --shell /bin/bash \
  && adduser $SWEDEB_USER sudo \
  && echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive
ENV LD_LIBRARY_PATH=/usr/local/lib

RUN apt update && apt upgrade -y  \
    && apt install -y --no-install-recommends software-properties-common \
    && apt-get install -y --no-install-recommends \
        perl \
        curl \
        bison flex libglib2.0-0 readline-common libncurses5 libreadline8 \
        perl less gzip bzip2 make git sudo \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/local
COPY --from=builder /tmp/cwb.bin.install.tar /tmp/cwb.bin.install.tar
COPY --from=builder /tmp/cwb.lib.install.tar /tmp/cwb.lib.install.tar
RUN tar xf /tmp/cwb.bin.install.tar -C /usr/local/bin \
    && tar xf /tmp/cwb.lib.install.tar -C /usr/local/lib \
    && rm -f /tmp/cwb.*.install.tar

VOLUME /data

WORKDIR /app

RUN chown -R ${SWEDEB_USER}:${SWEDEB_USER} /app /data

USER ${SWEDEB_USER}

ENV CORPUS_REGISTRY=/data/registry

RUN git clone https://github.com/humlab-swedeb/swedeb-demo.git .
RUN curl -sSL https://install.python-poetry.org | python3 -
RUN ~/.local/share/pypoetry/venv/bin/poetry config virtualenvs.create false
RUN ~/.local/share/pypoetry/venv/bin/poetry install --no-dev
RUN ~/.local/share/pypoetry/venv/bin/poetry export -f requirements.txt >> requirements.txt
RUN pip install -r requirements.txt

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "main_page_shared_filter.py",  "--server.port=8501", "--server.address=0.0.0.0"]


