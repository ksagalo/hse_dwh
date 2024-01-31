CREATE SCHEMA IF NOT EXISTS "dwh_detailed";
CREATE SCHEMA IF NOT EXISTS "presentation";

create table dwh_detailed.hub_categories
(
    category_pk   bytea primary key,
    category_id   integer,
    load_date     date,
    record_source text
);

create table dwh_detailed.hub_customers
(
    customer_pk   bytea primary key,
    customer_id   integer,
    load_date     date,
    record_source text
);

create table dwh_detailed.hub_deliveries
(
    delivery_pk   bytea primary key,
    delivery_id   bigint,
    load_date     date,
    record_source text
);

create table dwh_detailed.hub_manufacturers
(
    manufacturer_pk bytea primary key,
    manufacturer_id integer,
    load_date       date,
    record_source   text
);

create table dwh_detailed.hub_products
(
    product_pk    bytea primary key,
    product_id    bigint,
    load_date     date,
    record_source text
);

create table dwh_detailed.hub_purchases
(
    purchase_pk   bytea primary key,
    purchase_id   integer,
    load_date     date,
    record_source text
);

create table dwh_detailed.hub_stores
(
    store_pk      bytea primary key,
    store_id      integer,
    load_date     date,
    record_source text
);

create table dwh_detailed.link_product_category
(
    link_product_category_pk bytea primary key,
    category_pk              bytea,
    product_pk               bytea,
    load_date                date,
    record_source            text
);

create table dwh_detailed.link_product_delivery
(
    link_product_delivery_pk bytea primary key,
    delivery_pk              bytea,
    product_pk               bytea,
    load_date                date,
    record_source            text
);

create table dwh_detailed.link_product_manufacture
(
    link_product_manufacture_pk bytea primary key,
    manufacturer_pk             bytea,
    product_pk                  bytea,
    load_date                   date,
    record_source               text
);

create table dwh_detailed.link_purchase_customer
(
    link_customer_purchase_pk bytea primary key,
    purchase_pk               bytea,
    customer_pk               bytea,
    load_date                 date,
    record_source             text
);

create table dwh_detailed.link_purchase_product
(
    link_product_purchase_pk bytea primary key,
    purchase_pk              bytea,
    product_pk               bytea,
    load_date                date,
    record_source            text
);

create table dwh_detailed.link_purchase_store
(
    link_store_purchase_pk bytea primary key,
    purchase_pk            bytea,
    store_pk               bytea,
    load_date              date,
    record_source          text
);

create table dwh_detailed.sat_category
(
    category_pk       bytea primary key,
    category_hashdiff bytea,
    category_name     varchar(100),
    effective_from    timestamp,
    load_date         date,
    record_source     text
);

create table dwh_detailed.sat_customer
(
    customer_pk       bytea primary key,
    customer_hashdiff bytea,
    customer_first_name    varchar(100),
    customer_last_name    varchar(100),
    customer_gender   varchar(100),
    customer_phone    varchar(100),
    effective_from    timestamp,
    load_date         date,
    record_source     text
);

create table dwh_detailed.sat_delivery
(
    delivery_pk       bytea primary key,
    delivery_hashdiff bytea,
    delivery_date     date,
    product_count     integer,
    effective_from    date,
    load_date         date,
    record_source     text
);

create table dwh_detailed.sat_manufacture
(
    manufacturer_pk           bytea primary key,
    manufacturer_hashdiff     bytea,
    manufacturer_name         varchar(100),
    manufacturer_legal_entity varchar(100),
    effective_from            timestamp,
    load_date                 date,
    record_source             text
);

create table dwh_detailed.sat_product
(
    product_pk          bytea primary key,
    product_hashdiff    bytea,
    product_name        varchar(255),
    product_picture_url varchar(255),
    product_description varchar(255),
    product_age_restriction integer,
    product_price       numeric(9, 2),
    effective_from      timestamp,
    load_date           date,
    record_source       text
);

create table dwh_detailed.sat_purchase
(
    purchase_pk           bytea primary key,
    purchase_hashdiff     bytea,
    purchase_date         timestamp,
    purchase_payment_type varchar(100),
    product_count         bigint,
    product_price         numeric(9, 2),
    effective_from        timestamp,
    load_date             date,
    record_source         text
);

create table dwh_detailed.sat_store
(
    store_pk       bytea primary key,
    store_hashdiff bytea,
    store_name     varchar(255),
    store_country  varchar(255),
    store_city     varchar(255),
    store_address  varchar(255),
    effective_from timestamp,
    load_date      date,
    record_source  text
);

create table IF NOT EXISTS presentation.top_customers
(
    created_at        timestamp,
    customer_id       int,
    customer_gmv      DECIMAL(9, 2),
    customer_category varchar(255),
    customer_group    varchar(5)
);

create table IF NOT EXISTS presentation.categories
(
    created_at        timestamp,
    business_date     DATE,
    customer_category varchar(255),
    customer_gmv      DECIMAL(9, 2)
);

ALTER TABLE dwh_detailed.link_product_manufacture
ADD CONSTRAINT fk_manufacturer_key
FOREIGN KEY ("manufacturer_key")
REFERENCES dwh_detailed.hub_manufacturers("manufacturer_key");

ALTER TABLE dwh_detailed.link_product_manufacture
ADD CONSTRAINT fk_product_key
FOREIGN KEY ("product_key")
REFERENCES dwh_detailed.hub_products("product_key");

ALTER TABLE dwh_detailed.link_product_category
ADD CONSTRAINT fk_product_key
FOREIGN KEY ("product_key")
REFERENCES dwh_detailed.hub_products("product_key");

ALTER TABLE dwh_detailed.link_product_category
ADD CONSTRAINT fk_category_key
FOREIGN KEY ("category_key")
REFERENCES dwh_detailed.hub_categories("category_key");

ALTER TABLE dwh_detailed.link_product_delivery
ADD CONSTRAINT fk_product_key
FOREIGN KEY ("product_key")
REFERENCES dwh_detailed.hub_products("product_key");

ALTER TABLE dwh_detailed.link_product_delivery
ADD CONSTRAINT fk_delivery_key
FOREIGN KEY ("delivery_key")
REFERENCES dwh_detailed.hub_deliveries("delivery_key");

ALTER TABLE dwh_detailed.link_purchase_product
ADD CONSTRAINT fk_purchase_key
FOREIGN KEY ("purchase_key")
REFERENCES dwh_detailed.hub_purchases("purchase_key");

ALTER TABLE dwh_detailed.link_purchase_product
ADD CONSTRAINT fk_product_key
FOREIGN KEY ("product_key")
REFERENCES dwh_detailed.hub_products("product_key");

ALTER TABLE dwh_detailed.link_purchase_customer
ADD CONSTRAINT fk_purchase_key
FOREIGN KEY ("purchase_key")
REFERENCES dwh_detailed.hub_purchases("purchase_key");

ALTER TABLE dwh_detailed.link_purchase_customer
ADD CONSTRAINT fk_customer_key
FOREIGN KEY ("customer_key")
REFERENCES dwh_detailed.hub_customers("customer_key");

ALTER TABLE dwh_detailed.link_purchase_store
ADD CONSTRAINT fk_purchase_key
FOREIGN KEY ("purchase_key")
REFERENCES dwh_detailed.hub_purchases("purchase_key");

ALTER TABLE dwh_detailed.link_purchase_store
ADD CONSTRAINT fk_store_key
FOREIGN KEY ("store_key")
REFERENCES dwh_detailed.hub_stores("store_key");

ALTER TABLE dwh_detailed.sat_manufacture
ADD CONSTRAINT fk_manufacturer_key
FOREIGN KEY ("manufacturer_key")
REFERENCES dwh_detailed.hub_manufacturers("manufacturer_key");

ALTER TABLE dwh_detailed.sat_category
ADD CONSTRAINT fk_category_key
FOREIGN KEY ("category_key")
REFERENCES dwh_detailed.hub_categories("category_key");

ALTER TABLE dwh_detailed.sat_store
ADD CONSTRAINT fk_store_key
FOREIGN KEY ("store_key")
REFERENCES dwh_detailed.hub_stores("store_key");

ALTER TABLE dwh_detailed.sat_customer
ADD CONSTRAINT fk_customer_key
FOREIGN KEY ("customer_key")
REFERENCES dwh_detailed.hub_customers("customer_key");

ALTER TABLE dwh_detailed.sat_delivery
ADD CONSTRAINT fk_delivery_key
FOREIGN KEY ("delivery_key")
REFERENCES dwh_detailed.hub_deliveries("delivery_key");

ALTER TABLE dwh_detailed.sat_product
ADD CONSTRAINT fk_product_key
FOREIGN KEY ("product_key")
REFERENCES dwh_detailed.hub_products("product_key");

ALTER TABLE dwh_detailed.sat_purchase
ADD CONSTRAINT fk_purchase_key
FOREIGN KEY ("purchase_key")
REFERENCES dwh_detailed.hub_purchases("purchase_key");
