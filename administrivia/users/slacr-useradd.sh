#!/bin/bash

# slacr-useradd.sh -- pipecork
# Does everything to add cluster user, comments explain what and why.
# Make sure to run on the NIS server (slacr).

# ----- USAGE ------------------------------------------------
# to add user: 
#         ./slacr-useradd.sh <username> [<primary group (default: cluster)>]
#
# to baleet user: 
#         ./slacr-useradd.sh --remove <username>
# ------------------------------------------------------------


# If any one command fails, exit the script
set -e

# User home directories are stored where?
USERDIR=/home/osl/
# Traditionally, users' primary group is cluster. I don't know why it's not users.
GROUP=cluster


# Makes sure you're running this as root
if [ $(whoami) != 'root' ]; then
  echo "You should probably be running this as root bro."
  exit 1

# Code to remove user and their homedir
elif [[ $1 == '--remove' ]]; then
  if [ -z $2 ]; then
    echo "Remove whom?"
    exit 1
  fi

  read -p "Are you sure? Type the username again to confirm: " -r
  echo
  if [[ $REPLY == $2 ]]; then
    echo "Deleting user and their homedir..."
    userdel -r $2
    echo "Recompiling NIS..."
    make -C /var/yp
    
    EPITAPH=`echo $2 | sed  -e :a -e 's/^.\{1,30\}$/ & /;ta'` # "a pretty pity"
    IFS=%
    RIP=$" 
     _.---,._,' 
    /' _.--.<              we will always
      /'     ''             remember you
    /' _.---._____$EPITAPH
    \\.'   ___, .-'' 
        /'    \\\\             
      /'       '-.         -|-
     |                      |
     |                  .-'~~~'-.
     |                 .'       '.
     |                 |  R I P  |
     |                 |         |
     |                 |         |
      \\              \\\\\|         |//
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    "
    echo -e $RIP
    echo -e $RIP >> /var/log/rip.log  # The graveyard of our lost ones
    unset IFS

    exit
  else
    echo "Usernames did not match, aborting."
    exit
  fi

# Help/usage
elif [ -z $1 ] || [[ $1 == -* ]]; then 
  echo "SLACR useradd script (to be run as root on the NIS server)"
  echo "adds a new user to NIS, then makes and adds ssh key pairs for them."
  echo "       USAGE:  $0 <username> [<primary group (default: $GROUP)>]"
  echo "   TO REMOVE:  $0 --remove <username>"
  exit 1

# Actually add the user
else
  if [ $2 ]; then  # If group was specified, set it
    GROUP=$2
  fi
  
  # Set some handy vars
  USER=$1
  HOMEDIR=$USERDIR$USER

  # add the user to passwd and shadow
  # sets the user's home dir and group appropriately
	echo Adding user $USER to group $GROUP
	useradd -b $USERDIR -g $GROUP $USER

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
	su -c 'cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys' - $USER
  chmod 700 $HOMEDIR/.ssh
  chmod 600 $HOMEDIR/.ssh/*
  chmod 644 $HOMEDIR/.ssh/id_rsa.pub

	# push new data to all nodes and we're done
  echo Compiling NIS...
	make -C /var/yp

  # Make sure the machine actually thinks the user exists
  if id -u $USER >/dev/null 2>&1; then
    echo -e "\nDone! Test it out by logging in or sshing as $USER. Enjoy the new account!\n"
    exit 0
  else
    echo "Something went wrong; the machine doesn't think the user exists."
    echo "Check /etc/passwd and see what's up."
    exit 1
  fi
fi

exit
