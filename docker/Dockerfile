FROM ubuntu:20.04 AS base
ARG DEBIAN_FRONTEND=noninteractive

# installing basic apt dependencies and python3.7
RUN apt-get update -q \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends tzdata \
    && apt-get install -y --no-install-recommends \
	git htop mc links wget vim sudo screen ca-certificates \
    && sudo update-ca-certificates \
    && sudo apt-get install -y --no-install-recommends software-properties-common \
    && sudo add-apt-repository -y ppa:deadsnakes/ppa \
    && sudo apt-get install -y --no-install-recommends python3.7 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# set the locale and shell to prevent weird errors
ENV LANG C.UTF-8
SHELL ["/bin/bash", "-c"]

# cloning the Tournesol repository
WORKDIR /
# RUN git clone --recursive https://github.com/tournesol-app/tournesol.git
RUN git clone --recursive https://github.com/sergeivolodin/tournesol.git
WORKDIR /tournesol
RUN git checkout issue-dockerfile

# installing all Tournesol dependencies into a virtual environment
RUN ./setup.sh \
 && pip cache purge \
 && rm -rf ~/.cache/pip/ \
 && echo "source /tournesol/venv-tournesol/bin/activate" >> ~/.bashrc

# use installed firefox
ENV PATH /tournesol/firefox:$PATH

# creating ssh key
RUN ssh-keygen -f /root/.ssh/id_rsa -N "" \
 && echo "=== YOUR ssh public key is below, add it to your github ===" \
 && cat /root/.ssh/id_rsa.pub \
 && echo "=== /public key ===" \
 && git remote rm origin \
 && git remote add origin git@github.com:tournesol-app/tournesol.git

# web server port
EXPOSE 8000

# running tests
CMD bash ./tests.sh
