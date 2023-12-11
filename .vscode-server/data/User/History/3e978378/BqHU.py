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
    return temp_in_fahrenheit

#transform the data
def transform_load_data(task_instance):
    data = task_instance.xcom_pull(task_id="extract_weather_data")
    city = data["name"]
    weather_description = data["weather"][0]["description"]
    temp_fahrenheit = kelvin_to_fahrenheit(data["main"]["temp"])
    feels_like_fahrenheit = kelvin_to_fahrenheit(data["main"]["feels_like"])
    min_temp_fahrenheit = kelvin_to_fahrenheit(data["main"]["temp_min"])
    max_temp_fahrenheit = kelvin_to_fahrenheit(data["main"]["temp_max"])
    pressure = data["main"]["pressure"]
    humidity = data["main"]["humidity"]
    wind_speed = data["wind"]["speed"]
    time_of_record = datetime.utcfromtimestamp(data["dt"] + data["timezone"])
    sunrise_time = datetime.utcfromtimestamp(data["sys"]["sunrise"] + data["timezone"])
    sunset_time = datetime.utcfromtimestamp(data["sys"]["sunset"] + data["timezone"])

    transformed_data = {"City": city,
                        "Description": weather_description,
                        "Temperature (F)": temp_fahrenheit,
                        "Feels Like (F)": feels_like_fahrenheit,
                        "Minimum Temperature (F)": min_temp_fahrenheit,
                        "Maximum Temperature (F)": max_temp_fahrenheit,
                        "Pressure": pressure,
                        "Humidity": humidity,
                        "Wind Speed": wind_speed,
                        "Time of Record": time_of_record,
                        "Sunrise (Local Time)": sunrise_time,
                        "Sunset (Local Time)": sunset_time
    }

    transformed_data_list = [transformed_data]
    df_data = pd.DataFrame(transformed_data_list)

    now = dattime.now()
    dt_string = now.strftime()


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


