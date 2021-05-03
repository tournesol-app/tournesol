FROM ubuntu:20.04 AS base
ARG DEBIAN_FRONTEND=noninteractive

# installing basic apt dependencies
RUN apt-get update -q \
    && apt-get install -y --no-install-recommends \
	git htop mc links wget vim sudo screen \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# set the locale to prevent weird errors
ENV LANG C.UTF-8

# installing miniconda to have the right python version
# based on https://hub.docker.com/r/continuumio/miniconda3/dockerfile
# and https://github.com/HumanCompatibleAI/better-adversarial-defenses/blob/master/Dockerfile
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-4.5.11-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh && \
    /opt/conda/bin/conda clean -tipsy && \
    ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
    echo "conda activate base" >> ~/.bashrc
SHELL ["/bin/bash", "-c"]
ENV PATH /opt/conda/bin:$PATH

# cloning the Tournesol repository
WORKDIR /
RUN git clone --recursive https://github.com/tournesol-app/tournesol.git
WORKDIR /tournesol

# installing python 3.7
RUN conda update conda -y \
 && conda install -y python=3.7 \
 && conda clean --all -y

# installing all Tournesol dependencies into a virtual environment
RUN ./setup.sh \
 && pip cache purge \
 && rm -rf ~/.cache/pip/
 && echo "source /tournesol/venv-tournesol/bin/activate" >> ~/.bashrc

# web server port
EXPOSE 8000

# running tests
CMD bash ./tests.sh
