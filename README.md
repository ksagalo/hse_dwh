This project is build using docker copose. In the docker compose we define posetgres 14.5 version and will have master node and slave repplica.

There are script that runs as initialization of master node called db_init.sql Also - there are several .sh scripts and config files for master and slave in init_script directory

backup_master.sh - master backup for replication process create-replica-user.sh - creating replica slot if not exists otherwise take exists replica slot init-slave.sh - copying configs into slave node

init.sh - script that orchestrating that moves on server

in the docker compose .yml file we define volumes we copy on the server so it will be visible for server, names, ports

raise master node start replication process start slave node

