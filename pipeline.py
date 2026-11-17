import logging
import os

import pandas as pd
import requests
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

API_URL = 'https://api.open-meteo.com/v1/forecast'
PARAMS = {
    'latitude': 11.0168,
    'longitude': 76.9558,
    'hourly': 'temperature_2m,relative_humidity_2m,precipitation',
    'past_days': 7,
    'forecast_days': 1,
    'timezone': 'Asia/Kolkata',
}


def extract() -> dict:
    logging.info('Extracting data from API')
    response = requests.get(API_URL, params=PARAMS, timeout=30)
    response.raise_for_status()
    return response.json()


def transform(raw: dict) -> pd.DataFrame:
    logging.info('Transforming data')
    df = pd.DataFrame(raw['hourly'])
    df = df.rename(columns={
        'time': 'recorded_at',
        'temperature_2m': 'temperature_c',
        'relative_humidity_2m': 'humidity_pct',
        'precipitation': 'rain_mm',
    })
    df['recorded_at'] = pd.to_datetime(df['recorded_at'])
    df = df.dropna()
    df = df.drop_duplicates(subset='recorded_at')
    df['reading_date'] = df['recorded_at'].dt.date
    df['hour_of_day'] = df['recorded_at'].dt.hour
    return df


def get_engine():
    url = URL.create(
        'mysql+pymysql',
        username=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
    )
    return create_engine(url)


def load(df: pd.DataFrame) -> None:
    logging.info('Loading %d rows into MySQL', len(df))
    sql = text('''
        INSERT INTO weather_readings
            (recorded_at, reading_date, hour_of_day, temperature_c, humidity_pct, rain_mm)
        VALUES
            (:recorded_at, :reading_date, :hour_of_day, :temperature_c, :humidity_pct, :rain_mm)
        AS new
        ON DUPLICATE KEY UPDATE
            temperature_c = new.temperature_c,
            humidity_pct = new.humidity_pct,
            rain_mm = new.rain_mm
    ''')
    columns = ['recorded_at', 'reading_date', 'hour_of_day',
               'temperature_c', 'humidity_pct', 'rain_mm']
    records = df[columns].astype({'recorded_at': str, 'reading_date': str}).to_dict('records')
    with get_engine().begin() as conn:
        conn.execute(sql, records)
    logging.info('Load complete')


def main() -> None:
    raw = extract()
    clean = transform(raw)
    load(clean)


if __name__ == '__main__':
    main()