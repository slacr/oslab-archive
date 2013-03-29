# Hadoop Configurations

The JobTracker, slacr-bofur, is the task master.

The NameNode, slacr-bombur, is the distributed filesystem master.

They are also both slaves.

ori, dori, nori, and bifur are also slaves. They have different configurations
based on their cores and storage space.

Use "./hadoop_backup.sh <servername>" to quickly backup the conf for that server.
It requires rsync and puts the hadoop configuration directory in
<servername>/etc_hadoop
