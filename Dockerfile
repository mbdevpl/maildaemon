FROM mbdevpl/usable-ubuntu:latest

MAINTAINER Mateusz Bysiek <mateusz.bysiek.spam@gmail.com>

RUN sudo apt update && sudo apt install -y vagrant

WORKDIR /home/user/Projects

RUN git clone https://github.com/mbdevpl/DovecotTesting

COPY . /home/user/Projects/maildaemon
