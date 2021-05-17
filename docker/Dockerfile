FROM ubuntu:20.04 AS base
ARG DEBIAN_FRONTEND=noninteractive

# installing basic apt dependencies and python3.7
RUN echo "Installing APT dependencies" \
 && DEBIAN_FRONTEND=noninteractive apt-get update -q \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends git htop mc links wget vim sudo screen ca-certificates tzdata software-properties-common apt-utils libgtk-3-0 \
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
RUN git clone --recursive https://github.com/tournesol-app/tournesol.git
WORKDIR /tournesol

# installing all Tournesol dependencies into a virtual environment
RUN DEBIAN_FRONTEND=noninteractive ./setup.sh \
 && echo "echo 'Tournesol Debug Environment'" >> ~/.bashrc \
 && echo "source /tournesol/venv-tournesol/bin/activate" >> ~/.bashrc \
 && echo "source /tournesol/debug_export.sh" >> ~/.bashrc

# use installed firefox
ENV PATH /tournesol/firefox:/usr/bin:$PATH

# finalizing the setup
RUN sudo apt-get install -y openssh-client telnet net-tools x11vnc openssh-server \
 && ssh-keygen -f /root/.ssh/id_rsa -N "" \
 && git remote rm origin \
 && git remote add origin git@github.com:tournesol-app/tournesol.git \
 && git remote add origin_https https://github.com/tournesol-app/tournesol.git \
 && echo "PermitRootLogin yes" >> /etc/ssh/sshd_config \
 && echo "sudo service ssh start" >> ~/.bashrc \
 && echo "PATH=/tournesol/firefox:\$PATH" >> ~/.bashrc \
 && echo "root password is: tournesol" \
 && echo -e "tournesol\ntournesol" | passwd root

RUN echo "Creating the database" \
 && . ./debug_export.sh \
 && . ./venv-tournesol/bin/activate \
 && cd backend; python manage.py migrate

RUN echo "Building front-end" \
 && cd frontend; npm run build 

RUN echo "Adding the greeting message" \
 && sudo apt-get install -y cowsay lolcat \
 && sed -i 's/#force_color_prompt=yes/force_color_prompt=yes/g' /root/.bashrc \
 && sed -i 's/1;32m/1;93m/g' /root/.bashrc \
 && echo "Tournesol Docker Development Image, built on $(date)" | /usr/bin/tee -a /etc/motd \
 && echo "Let's build recommender systems together!" | /usr/games/cowthink -f moose | /usr/bin/tee -a /etc/motd \
 && echo "* To open the container, run sudo docker run -p 8000:8000 -p 8899:8899 -p 5900:5900 -p 2222:22 -it tournesol-app/tournesol" | /usr/bin/tee -a /etc/motd \
 && echo "* To run tests, run ./tests.sh inside" | /usr/bin/tee -a /etc/motd \
 && echo "* To run the server, run ./launch_debug.sh inside" | /usr/bin/tee -a /etc/motd \
 && echo "* To edit files, connect to port 2222 via ssh (login root, password tournesol)" | /usr/bin/tee -a /etc/motd \
 && echo "Push your changes to a separate branch, and then create a PR on https://github.com/tournesol-app/tournesol" | /usr/bin/tee -a /etc/motd \
 && echo "Connect via port 8000 to the server, via port 8899 to the notebook, and via port 5900 to VNC for integration tests" | /usr/bin/tee -a /etc/motd \
 && echo -e "\n\n=== YOUR ssh PUBLIC KEY is below, add it to your github ===" | /usr/bin/tee -a /etc/motd \
 && cat /root/.ssh/id_rsa.pub | /usr/bin/tee -a /etc/motd \
 && echo -e "=== /public key ===\n\n" | /usr/bin/tee -a /etc/motd \
 && echo "cat /etc/motd | /usr/games/lolcat --force" | /usr/bin/tee -a /root/.bashrc

# web server port
EXPOSE 8000
EXPOSE 8899
EXPOSE 5900
EXPOSE 22
