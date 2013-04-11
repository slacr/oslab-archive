#!/bin/bash

# slacr-useradd.sh -- pipecork
# Does everything to add cluster user, comments explain what and why.
# Make sure to run on the NIS server (slacr).

# If any one command fails, exit the script
set -e

# User home directories are stored where?
USERDIR=/home/osl/
# Traditionally, users' primary group is cluster. I don't know why it's not users.
GROUP=cluster

if [ -z $1 ] || [[ $1 == -* ]]; then
  echo "SLACR useradd script (to be run as root on the NIS server)"
  echo "adds a new user to NIS, then makes and adds ssh key pairs for them."
  echo "    USAGE: $0 <username> [<primary group (default:$GROUP)>]"
  exit 1

elif [ $(whoami) != 'root' ]; then
  echo you should probably be running this as root bro.
  exit 1

else
  if [ $2 ]; then
    GROUP=$2
  fi
  
  USER=$1
  HOMEDIR=$USERDIR$USER

  # add the user to passwd and shadow
  # sets the user's home dir and group appropriately
	echo Adding user $USER to group $GROUP
	useradd -d $HOMEDIR -g $GROUP $USER

	# makes user's home dir
	echo Creating home directory $HOMEDIR
	mkdir $HOMEDIR
	chown --recursive $USER $HOMEDIR
	chgrp --recursive $GROUP $HOMEDIR

	# add user password
	passwd $USER

	# ssh-keygen makes a private/public key pair which will allow the user 
  # passwordless authentication to cluster nodes.

  # ssh-keygen will ask you for a password for your key pair. Enter a 
  # password (or not) and accept the defaults for the other questions.
	su -c 'ssh-keygen' - $USER
  echo Adding public key for user $USER to the lab machines
	cat $HOMEDIR/.ssh/id_rsa.pub >> $HOMEDIR/.ssh/authorized_keys
  chmod 700 $HOMEDIR/.ssh
  chmod 600 $HOMEDIR/.ssh/*

	# push new data to all nodes and we're done
  echo Compiling NIS...
	make -C /var/yp

  # make sure you test it!
  if id -u $USER >/dev/null 2>&1; then
    echo -e "\nDone! Test it out by logging in or sshing as $USER. Enjoy the new account!\n"
    exit 0
  else
    echo "Something went wrong; the machine doesn't think the user exists."
    echo "Check /etc/passwd and see what's up."
    exit 1
  fi
fi

