import json
from airflow import DAG
from datetime import timedelta, datetime
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.operators.python import PythonOperator
import pandas as pd


#convert kelvin to fahrenheit
def kelvin_to_fahrenheit(temp_in_kelvin):
    temp_in_fahrenheit = (temp_in_kelvin - 273.15) * (9/5) + 32

#transfor the data
def transform_load_weather_data(task_instance):
    data = task_instance.xcom_pull(task_id="extract_weather_data")
    city = data["name"]
    weather_description = 



default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    # 'start_date': datetime(2023, 12, 6),
    'start_date': datetime.now(),
    'email': ['sam@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=2)
}

with DAG('weather_dag',
    default_args=default_args,
    schedule_interval = '@daily',
    catchup=False) as dag:


#Check (poke) the endpoint to see it is working
    is_weather_api_ready = HttpSensor(
        task_id='is_weather_api_ready',
        http_conn_id='weathermap_api',
        endpoint='/data/2.5/weather?q=manchester&appid=2bef7eedf241799685e1126ac12e9c9d',
        # https://api.openweathermap.org/data/2.5/weather?q=manchester&appid=2bef7eedf241799685e1126ac12e9c9d
    )
#Checkout documentation for airflow http operators here:
# https://airflow.apache.org/docs/apache-airflow-providers-http/stable/operators.html

#Connect to the endpoint and obtain the data
    extract_weather_data = SimpleHttpOperator(
        task_id = 'extract_weather_data',
        http_conn_id = 'weathermap_api',
        endpoint='/data/2.5/weather?q=manchester&appid=2bef7eedf241799685e1126ac12e9c9d',
        method = 'GET',
        response_filter = lambda r: json.loads(r.text),
        log_response = True
    )

    transform_load_weather_data = PythonOperator(
        task_id = 'transform_load_weather_data',
        python_callable = transform_load_weather_data
    )

    is_weather_api_ready >> extract_weather_data


