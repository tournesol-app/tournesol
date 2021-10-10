FROM debian:bullseye

RUN apt update && \
    apt -y upgrade && \
    apt -y install software-properties-common gnupg curl
RUN curl "https://dl.yarnpkg.com/debian/pubkey.gpg" | gpg --dearmor > /usr/share/keyrings/yarnpkg-keyring.gpg  && \
    echo "deb [signed-by=/usr/share/keyrings/yarnpkg-keyring.gpg] https://dl.yarnpkg.com/debian/ stable main" > /etc/apt/sources.list.d/yarnpkg.list && \
    apt update && \
    apt -y install yarn

ARG NVM_VERSION="v0.38.0"
ARG NODE_VERSION="fermium"
RUN curl -o - "https://raw.githubusercontent.com/nvm-sh/nvm/$NVM_VERSION/install.sh" | NVM_DIR=/root/.nvm bash
RUN . ~/.nvm/nvm.sh && NVM_DIR=/root/.nvm nvm install --lts=$NODE_VERSION

COPY package.json /frontend/

RUN . ~/.nvm/nvm.sh && NVM_DIR=/root/.nvm nvm use lts/$NODE_VERSION && cd /frontend && yarn
