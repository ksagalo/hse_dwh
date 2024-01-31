This project is build using docker copose. In the docker compose we define posetgres 14.5 version and will have master node and slave repplica.

There are script that runs as initialization of master node called db.sql Also - there are several .sh scripts and config files for master and slave in init_script directory

backup_master.sh - master backup for replication process create-replica-user.sh - creating replica slot if not exists otherwise take exists replica slot init-slave.sh - copying configs into slave node

init.sh - script that orchestrating that moves on server

in the docker compose .yml file we define volumes we copy on the server so it will be visible for server, names, ports

to run whole cluster use docker-entrypoint.sh: includes>> cleaning data shutdown docker

raise master node start replication process start slave node

do some sql from hw1(create table gmv and make it view) on the slave node

#############HW2##############

Added data to init ddl script
organized debezium for postgresql: debezium connected to masterhost and used to run zookeeper(zookeeper) that need to run kafka broker(service - broker) to write messages and make well separated structure for easy instanciated and growing database system
as mentioned in: https://debezium.io/documentation/reference/stable/tutorial.html https://hub.docker.com/r/debezium/zookeeper/ https://debezium.io/documentation/reference/stable/connectors/postgresql.html#debezium-connector-for-postgresql
new instance of postgresql running via command in docker-entrypoint.sh
