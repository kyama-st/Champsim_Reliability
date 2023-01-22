FROM debian:stable

# These commands copy your files into the specified directory in the image
# and set that as the working location

# This command compiles your app using GCC, adjust for your source code
# RUN g++ -o myapp main.cpp
RUN apt-get update && \
    apt-get install -y build-essential cmake clang libssl-dev

# This command runs your application, comment out this line to compile only
# CMD ["./run_champsim.sh"]
# CMD ["./myapp"]

ARG UNAME
ARG GNAME
ARG UID
ARG GID
RUN groupadd -g $GID -o $GNAME
# Add a user with empty password in sudo: https://unix.stackexchange.com/a/472968
RUN useradd -m -u $UID -g $GID -o -s /bin/bash $UNAME && echo "$UNAME:U6aMy0wojraho" | chpasswd -e && usermod -aG sudo $UNAME

# Set the user (for subsequent commands)
USER $UNAME

# Set the working directory (for subsequent commands)
# WORKDIR /home/$UNAME

WORKDIR /cars/Champsim_Reliability

CMD /bin/bash
LABEL Name=champsim Version=0.0.1
