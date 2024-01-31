echo "Clearing data"
rm -rf ./data
rm -rf ./data-slave
docker compose down -v

docker compose up -d postgres_master

echo "Starting postgres_master node..."
sleep 60  # Waits for master note start complete

echo "Prepare replica config..."
docker exec -it postgres_master sh /etc/postgresql/init-script/init.sh

echo "Restart master node"
docker compose restart postgres_master
sleep 30

echo "Starting slave node..."
docker compose up -d postgres_slave
sleep 30
echo "Done"

docker compose up -d postgres_dwh zookeeper broker debezium debezium-ui rest-proxy

curl -X POST --location "http://localhost:8083/connectors" -H "Content-Type: application/json" -H "Accept: application/json" -d @debezium/debezium.json
curl -X POST -H "Content-Type: application/vnd.kafka.v2+json" -H "Accept: application/vnd.kafka.v2+json" -d '{"name": "dwh", "format": "binary", "auto.offset.reset": "latest"}' http://localhost:8082/consumers/dwh

cd airflow && docker compose up -d
sleep 30  # wait
docker exec airflow-airflow-webserver-1 airflow connections add 'postgres_dwh' --conn-type 'postgres' \
sleep 60

cd .. && python3 consumer.py
