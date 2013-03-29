#!/bin/bash
# Find all open, ssh-able hosts in the computer center
# 1. Write out all live hosts in the network to a file
# 2. Filter out hosts with port 22 closed 
# 2a. Filter out only IP addresses

  # 1.
  nmap 10.14.10.0/24 10.14.20.0/24 -n -p22 -oG hosts.live

  # 2, 2a
  awk < hosts.live '/open/ { print $2 }' > hosts.p22.live
