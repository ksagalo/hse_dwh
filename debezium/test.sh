curl -X POST --location "http://localhost:8083/connectors" -H "Content-Type: application/json" -H "Accept: application/json" -d @debezium.json
curl -X POST -H "Content-Type: application/vnd.kafka.v2+json" -H "Accept: application/vnd.kafka.v2+json" -d '{"name": "dwh", "format": "binary", "auto.offset.reset": "latest"}' http://localhost:8082/consumers/dwh
