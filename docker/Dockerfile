FROM ubuntu:20.04 AS base
ARG DEBIAN_FRONTEND=noninteractive

# installing basic apt dependencies and python3.7
RUN echo "Installing APT dependencies" \
 && DEBIAN_FRONTEND=noninteractive apt-get update -q \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends git htop mc links wget vim sudo screen ca-certificates tzdata software-properties-common apt-utils \
 && DEBIAN_FRONTEND=noninteractive sudo update-ca-certificates \
 && DEBIAN_FRONTEND=noninteractive sudo add-apt-repository -y ppa:deadsnakes/ppa \
 && DEBIAN_FRONTEND=noninteractive sudo apt-get install -y --no-install-recommends python3.7 python3.7-venv python3.7-dev \
 && DEBIAN_FRONTEND=noninteractive apt-get clean

# installing pip
RUN echo "Installing PIP" \
 && wget -q https://bootstrap.pypa.io/get-pip.py -o get-pip.py \
 && python3.7 get-pip.py

# set the locale and shell to prevent weird errors
ENV LANG C.UTF-8
SHELL ["/bin/bash", "-c"]

# cloning the Tournesol repository
WORKDIR /
# RUN git clone --recursive https://github.com/tournesol-app/tournesol.git
RUN git clone --recursive https://github.com/sergeivolodin/tournesol.git tournesol
WORKDIR /tournesol
RUN git checkout issue-dockerfile

# installing all Tournesol dependencies into a virtual environment
RUN DEBIAN_FRONTEND=noninteractive ./setup.sh \
 && echo "echo 'Tournesol Debug Environment'" >> ~/.bashrc \
 && echo "source /tournesol/venv-tournesol/bin/activate" >> ~/.bashrc \
 && echo "source /tournesol/debug_export.sh" >> ~/.bashrc

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
