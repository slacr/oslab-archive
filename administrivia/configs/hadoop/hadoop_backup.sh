#!/bin/bash

if [ ! -f $1/ ]; then
    mkdir $1/
fi

rsync -r $1:/etc/hadoop $1/etc_hadoop
