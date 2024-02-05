from datetime import datetime
from sqlalchemy import create_engine, text
import pandas as pd
from airflow import DAG
from airflow.operators.python import PythonOperator

pg_engine = create_engine(
    'postgresql://postgres:postgres@localhost:5434/postgres')

dag_params = {
    'owner': 'airflow',
    'dag_id': 'category_gmv',
    'description': 'update of table gmv',
    'start_date': datetime(2024, 1, 15),
    'schedule_interval': '55 4 * * *',
    'catchup': False,
    'default_args': {
        'retries': 3,
    }
}


def presentation_update():
    with pg_engine.connect() as connection:
        connection.execute(
            '''delete from presentation.category_gmv where business_date = DATE(now()) - 1''')
    query = '''with actual_cat_sat as (select *
                                            from (
                                                     select *,
                                                            row_number() over (partition by category_pk order by effective_from desc) as rn
                                                     from dwh_detailed.sat_category) acs
                                            where rn = 1),
                         actual_purch_sat as (select *
                                              from (
                                                       select *,
                                                              row_number() over (partition by purchase_pk order by effective_from desc) as rn
                                                       from dwh_detailed.sat_purchase
                                                       where DATE(purchase_date) = DATE(now())-1) aps
                                              where rn = 1)

                    select now()                                                   as created_at,
                           DATE(now())-1                         as business_date,
                           scd.category_name                                       as category_name,
                           coalesce(sum(spd.product_price * spd.product_count), 0) as category_gmv
                    from dwh_detailed.link_product_category lpca
                             left join dwh_detailed.link_purchase_product lpp on lpp.product_pk = lpca.product_pk
                             left join actual_cat_sat scd on lpca.category_pk = scd.category_pk
                             left join actual_purch_sat spd on lpp.purchase_pk = spd.purchase_pk
                    group by DATE(spd.purchase_date), scd.category_name'''
    df = pd.read_sql(query, pg_engine)
    df.to_sql('category_gmv', pg_engine, if_exists="append",
              schema='presentation', index=False)


with DAG(**dag_params) as dag:
    category_gmv = PythonOperator(
        python_callable=presentation_update,
        dag=dag,
        task_id='category_gmv'
    )

    category_gmv
