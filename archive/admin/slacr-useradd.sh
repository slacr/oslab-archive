#!/bin/bash
# does everything to add cluster user, comments explain what and why.

# cluster home directories are stored where?
HOME=/home/osl

if [ $1 ]; then

	# add the user to passwd and shadow
	# and sets the user's home dir and group appropriately

	echo adding user $1
	useradd -d $HOME/$1 -g cluster $1


	# makes user's home dir

	echo creating home directory /home/slacr/$1
	mkdir $HOME/$1
	chown $1 $HOME/$1
	chgrp cluster $HOME/$1


	# add user password

	passwd $1


	# we need to add a certian config file to user's .ssh 
	# so we can ssh into machines we don't know (i.e. that
	# arent in ~/.ssh/known_hosts) w/o being asked any questions

	echo configing some shit @ u
	mkdir $HOME/$1/.ssh -m 0700
	chown $1 $HOME/$1/.ssh
	chgrp cluster $HOME/$1/.ssh
	echo -e "Host *\nStrictHostKeyChecking no" >> $HOME/$1/.ssh/config
	chown $1 $HOME/$1/.ssh/config
	chgrp cluster $HOME/$1/.ssh/config


	# ssh-keygen allows for passwordless authentication
	# user need only invoke 'ssh-agent bash' and then 'ssh-add',
	# type passphrase to unlock something, and then can ssh 
	# to all cluster nodes w/o password. 

	ssh-keygen -t dsa -f $HOME/$1/.ssh/id_dsa
	chown $1 $HOME/$1/.ssh/id_dsa
	chgrp cluster $HOME/$1/.ssh/id_dsa
	chown $1 $HOME/$1/.ssh/id_dsa.pub
	chgrp cluster $HOME/$1/.ssh/id_dsa.pub
	cat $HOME/$1/.ssh/id_dsa.pub >> $HOME/$1/.ssh/authorized_keys
	chown $1 $HOME/$1/.ssh/authorized_keys
	chgrp cluster $HOME/$1/.ssh/authorized_keys

	# push new data to all nodes and we're done

	make -C /var/yp

else
	echo "usage: ./slacr-useradd.sh <username>"
fi
