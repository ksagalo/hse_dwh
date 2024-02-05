from datetime import datetime
from sqlalchemy import create_engine, text
import pandas as pd
from airflow import DAG
from airflow.operators.python import PythonOperator

pg_engine = create_engine(
    'postgresql://postgres:postgres@localhost:5434/postgres')


dag_params = {
    'owner': 'airflow',
    'dag_id': 'customer_categories',
    'description': 'update of table cc',
    'start_date': datetime(2024, 1, 15),
    'schedule_interval': '55 4 * * *',
    'catchup': False,
    'default_args': {
        'retries': 3,
    }
}


def presentation_update():
    query = '''WITH customer_gmv AS (SELECT hb.customer_id,
                                        sum(sp.purchase_count * sp.product_price) AS total_sum
                                    FROM sat_purchase sp
                                      JOIN link_purchase_customer lpc ON lpc.purchase_key = sp.purchase_key
                                      JOIN hub_customers hb ON hb.customer_key = lpc.customer_key
                                      WHERE sp.load_date < date(now()
                                      GROUP BY lpc.customer_key),
            customer_group AS (SELECT customer_id,
                                            CASE 
                                                when total_sum / (sum(total_sum) over () + 0.001) > 0.95 THEN '5'
                                                when total_sum / (sum(total_sum) over () + 0.001) > 0.9 THEN '10'
                                                when total_sum / (sum(total_sum) over () + 0.001) > 0.75 THEN '25'
                                                when total_sum / (sum(total_sum) over () + 0.001) > 0.5 THEN '50'
                                                when total_sum / (sum(total_sum) over () + 0.001) > 0.95 THEN '5'
                                                ELSE '50+'
                                            END AS customer_group,
                                        FROM customer_gmv)
                                        ),
            customer_category AS (SELECT customer_id, category_name 
                                    FROM (SELECT customer_id,
                                                category_name,
                                                row_number() OVER (PARTITION BY customer_id ORDER BY total_sum DESC) AS rn
                                                FROM (SELECT hb.customer_id, 
                                                             sc.category_name,
                                                             sum(st.product_price * st.product_count) AS total_sum
                                                        FROM dwh_detailed.link_purchase_customer AS lpc
                                                        JOIN dwh_detailed.sat_purchase st ON lpc.purchase_key = st.purchase_key
                                                        JOIN dwh_detailed.hub_customers AS hb on lpc.customer_key = hb.customer_key
                                                        JOIN dwh_detailed.link_purchase_product AS lpp on lpc.purchase_key = lpp.purchase_key
                                                        JOIN dwh_detailed.link_product_category AS lpct on lpp.product_key = lpct.product_key
                                                        JOIN dwh_detailed.sat_category AS sc ON lpc.category_key = sc.category_key
                                                        GROUP BY hb.customer_id, sc.category_name) AS total_category) 
                                                        AS top_cat
                                                        WHERE rn = 1)
            
            SELECT now(),
                   hc.customer_id, 
                   cgm.total_sum AS customer_gmv,
                   cc.customer_category,
                   cg.customer_group
                   FROM hub_customers hc
                 JOIN customer_gmv cgm ON hc.customer_id = cgm.customer_id
                 JOIN customer_group cg ON hc.customer_id = cg.customer_id
                 JOIN customer_category cc ON hc.customer_id = cc.customer_id'''
    df = pd.read_sql(query, pg_engine)
    df.to_sql('customers_categories', pg_engine, if_exists="append",
              schema='presentation', index=False)


with DAG(**dag_params) as dag:
    customer_categories = PythonOperator(
        python_callable=presentation_update,
        dag=dag,
        task_id='customer_categories'
    )

    customer_categories

