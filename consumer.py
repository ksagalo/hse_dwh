import hashlib
import datetime
from datetime import date
from sqlalchemy import create_engine, text
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import Consumer
import json
import pandas as pd


pg_engine = create_engine(
    'postgresql://postgres:postgres@localhost:5434/postgres')


def compute_hash(*args):
    return hashlib.md5(''.join(str(arg) for arg in args).encode()).hexdigest()


def insert_row(table_name, data_dict, engine=pg_engine):
    df = pd.DataFrame([data_dict])
    df.to_sql(table_name, engine, if_exists='append', schema='dwh_detailed',
              index=False)


def category(before, after):
    category_attributes = {
        "category_key": compute_hash(after["category_id"]),
        "category_hash_diff": compute_hash(after["category_id"],
                                            after["category_name"]),
        "category_name": after["category_name"],
        "effective_from": date.today(),
        "load_date": date.today(),
        "record_source": "3NF"
    }
    insert_row('sat_category', category_attributes)

    if not before:
        hub_data = {
            "category_key": compute_hash(after["category_id"]),
            "category_id": after["category_id"],
            "load_date": date.today(),
            "record_source": "3NF"
        }
        insert_row('hub_categories', hub_data)


def manufacturer(before, after):
    manufacturer_attributes = {
        "manufacturer_key": compute_hash(after["manufacturer_id"]),
        "manufacturer_hash_diff": compute_hash(after["manufacturer_id"],
                                                after["manufacturer_name"],
                                                after["manufacturer_legal_entity"]),
        "manufacturer_name": after["manufacturer_name"],
        "manufacturer_legal_entity": after["manufacturer_legal_entity"],
        "effective_from": date.today(),
        "load_date": date.today(),
        "record_source": "3NF"
    }
    insert_row('sat_manufacturer', manufacturer_attributes)

    if not before:
        hub_data = {
            "manufacturer_key": compute_hash(after["manufacturer_id"]),
            "manufacturer_id": after["manufacturer_id"],
            "load_date": date.today(),
            "record_source": "3NF"
        }
        insert_row('hub_manufacturers', hub_data)


def product(before, after):
    product_attributes = {
        "product_key": compute_hash(after["product_id"]),
        "product_hash_diff": compute_hash(after["product_id"],
                                           after["product_name"],
                                           after["product_picture_url"],
                                           after["product_description"],
                                           after["product_restriction"]),
        "product_name": after["product_name"],
        "product_picture_url": after["product_picture_url"],
        "product_description": after["product_description"],
        "product_restriction": after["product_restriction"],
        "product_price": None,
        "effective_from": date.today(),
        "load_date": date.today(),
        "record_source": "3NF"
    }
    insert_row('sat_product', product_attributes)
    if not before:
        hub_data = {
            "product_key": compute_hash(after["product_id"]),
            "product_id": after["product_id"],
            "load_date": date.today(),
            "record_source": "3NF"
        }
        insert_row('hub_products', hub_data)
        link_product_category_data = {
            "link_product_category_key": compute_hash(after["product_id"],
                                                       after["category_id"]),
            "product_key": compute_hash(after["product_id"]),
            "category_key": compute_hash(after["category_id"]),
            "load_date": date.today(),
            "record_source": "3NF"
        }
        insert_row('link_product_category', link_product_category_data)
        link_product_manufacture_data = {
            "link_product_manufacture_key": compute_hash(after["product_id"],
                                                          after[
                                                              "category_id"]),
            "product_key": compute_hash(after["product_id"]),
            "manufacturer_key": compute_hash(after["manufacturer_id"]),
            "load_date": date.today(),
            "record_source": "3NF"
        }
        insert_row('link_product_manufacture', link_product_manufacture_data)


def store(before, after):
    store_attributes = {
        "store_key": compute_hash(after["store_id"]),
        "store_hash_diff": compute_hash(after["store_id"],
                                         after["store_name"],
                                         after["store_country"],
                                         after["store_city"],
                                         after["store_address"]),
        "store_name": after["store_name"],
        "store_country": after["store_country"],
        "store_city": after["store_city"],
        "store_address": after["store_address"],
        "effective_from": date.today(),
        "load_date": date.today(),
        "record_source": "3NF"
    }
    insert_row('sat_store', store_attributes)
    if not before:
        # hub
        hub_data = {
            "store_key": compute_hash(after["store_id"]),
            "store_id": after["store_id"],
            "load_date": date.today(),
            "record_source": "3NF"
        }
        insert_row('hub_stores', hub_data)


def customer(before, after):
    customer_attributes = {
        "customer_key": compute_hash(after["customer_id"]),
        "customer_hash_diff": compute_hash(after["customer_id"],
                                            after["customer_first_name"],
                                            after["customer_last_name"],
                                            after["customer_gender"],
                                            after["customer_phone"]),
        "customer_first_name": after["customer_first_name"],
        "customer_last_name": after["customer_last_name"],
        "customer_gender": after["customer_gender"],
        "customer_phone": after["customer_phone"],
        "effective_from": date.today(),
        "load_date": date.today(),
        "record_source": "3NF"
    }
    insert_row('sat_customer', customer_attributes)
    if not before:
        hub_data = {
            "customer_key": compute_hash(after["customer_id"]),
            "customer_id": after["customer_id"],
            "load_date": date.today(),
            "record_source": "3NF"
        }
        insert_row('hub_customers', hub_data)


def purchase(after):
    existing_record = pd.read_sql(f"""
        SELECT * FROM dwh_detailed.sat_purchase
        WHERE purchase_key = '{compute_hash(after["purchase_id"])}'
        ORDER BY effective_from DESC
        LIMIT 1""", pg_engine).to_dict('records')
    current_purchase = existing_record[0] if existing_record \
        else {key: None for key in ["purchase_key", "purchase_hash_diff",
                                    "purchase_date",
                                    "purchase_payment_type",
                                    "product_count",
                                    "product_price",
                                    "effective_from",
                                    "load_date",
                                    "record_source"
                                    ]}

    is_new_purchase = current_purchase["purchase_key"] is None
    if "store_id" in after and is_new_purchase:
        link_store_purchase_data = {
            "link_store_purchase_key": compute_hash(after["store_id"],
                                                     after["purchase_id"]),
            "store_key": compute_hash(after["store_id"]),
            "purchase_key": compute_hash(after["purchase_id"]),
            "load_date": date.today(),
            "record_source": "3NF"
        }
        insert_row('link_purchase_store', link_store_purchase_data)
    if (current_purchase["product_count"] is None
        or current_purchase["product_count"] == 0) and "product_id" in after.keys():
        link_customer_purchase_data = {
            "link_customer_purchase_key": compute_hash(after["purchase_id"],
                                                        after["customer_id"]),
            "purchase_key": compute_hash(after["purchase_id"]),
            "customer_key": compute_hash(after["customer_id"]),
            "load_date": date.today(),
            "record_source": "3NF"
        }
        insert_row('link_purchase_customer', link_customer_purchase_data)
        current_purchase.update({(k, v) for k, v in after.items() if
                                 k in ['product_count', 'product_price',
                                       'purchase_id',
                                       'purchase_date',
                                       'purchase_payment_type']})
    purchase_attributes = {
        "purchase_key": compute_hash(after["purchase_id"]),
        "purchase_hash_diff": compute_hash(current_purchase["purchase_id"],
                                            current_purchase["purchase_date"],
                                            current_purchase[
                                                "purchase_payment_type"],
                                            current_purchase["product_count"],
                                            current_purchase["product_price"]),
        "purchase_date": datetime.fromtimestamp(
            current_purchase["purchase_date"] // 1000000)
        if isinstance(current_purchase["purchase_date"], int) else current_purchase["purchase_date"],
        "purchase_payment_type": current_purchase["purchase_payment_type"],
        "product_count": current_purchase["product_count"],
        "product_price": current_purchase["product_price"],
        "effective_from": date.today(),
        "load_date": date.today(),
        "record_source": "3NF"
    }
    insert_row('sat_purchase', purchase_attributes)
    if is_new_purchase:
        hub_data = {
            "purchase_key": compute_hash(after["purchase_id"]),
            "purchase_id": after["purchase_id"],
            "load_date": date.today(),
            "record_source": "3NF"
        }
        insert_row('hub_purchases', hub_data)


def delivery(before, after):
    delivery_hash = compute_hash(after["delivery_id"])
    delivery_attributes = {
        "delivery_key": compute_hash(after["delivery_id"]),
        "delivery_hash_diff": compute_hash(after["delivery_id"],
                                            after["delivery_date"],
                                            after["product_count"]),
        "delivery_date": datetime.datetime.utcfromtimestamp(0) + datetime.timedelta(after["delivery_date"]),
        "product_count": after["product_count"],
        "effective_from": date.today(),
        "load_date": date.today(),
        "record_source": "3NF"
    }
    insert_row('sat_delivery', delivery_attributes)
    if not before:
        hub_data = {
            "delivery_key": delivery_hash,
            "delivery_id": after["delivery_id"],
            "load_date": date.today(),
            "record_source": "3NF"
        }
        insert_row('hub_deliveries', hub_data)
        link_product_delivery_data = {
            "link_product_delivery_key": compute_hash(after["product_id"],
                                                       after["delivery_id"]),
            "product_key": compute_hash(after["product_id"]),
            "delivery_key": compute_hash(after["delivery_id"]),
            "load_date": date.today(),
            "record_source": ["3NF"]
        }
        insert_row('link_product_delivery', link_product_delivery_data)


def price_change(after):
    records = pd.read_sql(f"""
        SELECT * FROM dwh_detailed.sat_product
        WHERE product_key = '{compute_hash(after["product_id"])}' 
        ORDER BY effective_from DESC 
        LIMIT 1""", pg_engine).to_dict('records')
    old = records[0]
    new = after["new_price"]
    product_attributes = {
        "product_key": compute_hash(after["product_id"]),
        "product_hash_diff": compute_hash(
            after["product_id"],
            old["product_name"],
            old["product_picture_url"],
            old["product_description"],
            old["product_restriction"],
            new),
        "product_name": old["product_name"],
        "product_picture_url": old["product_picture_url"],
        "product_description": old["product_description"],
        "product_restriction": old["product_restriction"],
        "product_price": new,
        "effective_from": datetime.datetime.fromtimestamp(after['price_change_ts'] // 1000000),
        "load_date": date.today(),
        "record_source": "3NF"
    }
    insert_row('sat_product', product_attributes)


def consume_loop(consumer, topics):
    try:
        consumer.subscribe(topics)
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            elif msg.error():
                print(f"Consume error: {msg.value()}")
                continue
            else:
                value = json.loads(msg.value().decode('utf-8'))['payload']
                before = value["before"]
                after = value["after"]
                if msg.topic() == "postgres.system.categories":
                    category(before, after)
                elif msg.topic() == "postgres.system.manufacturers":
                    manufacturer(before, after)
                elif msg.topic() == "postgres.system.products":
                    product(before, after)
                elif msg.topic() == "postgres.system.stores":
                    store(before, after)
                elif msg.topic() == "postgres.system.customers":
                    customer(before, after)
                elif msg.topic() == "postgres.system.purchases":
                    purchase(after)
                elif msg.topic() == "postgres.system.purchase_items":
                    purchase(after)
                elif msg.topic() == "postgres.system.deliveries":
                    delivery(before, after)
                elif msg.topic() == "postgres.system.price_change":
                    price_change(after)

    finally:
        consumer.close()


def main():
    topics = [
        "postgres.public.categories",
        "postgres.public.customers",
        "postgres.public.deliveries",
        "postgres.public.manufacturers",
        "postgres.public.price_change",
        "postgres.public.products",
        "postgres.public.purchase_items",
        "postgres.public.purchases",
        "postgres.public.stores"
    ]
    admin_client = AdminClient({
        "bootstrap.servers": "broker:29092"
    })
    fs = admin_client.create_topics([NewTopic(topic, 1, 1) for topic in topics])
    conf = {'bootstrap.servers': 'broker:29092',
            'group.id': 'dwh',
            'enable.auto.commit': False,
            'auto.offset.reset': 'latest'}
    consumer = Consumer(conf)
    consume_loop(consumer, topics)


if __name__ == "__main__":
    main()
