import pandas as pd
import psycopg2
from dotenv import load_dotenv
import os

# .env 불러오기
load_dotenv()
dsn = os.getenv("DB_URL")

# 연결
conn = psycopg2.connect(dsn)

# 쿼리 → DataFrame → CSV 저장
df = pd.read_sql_query("SELECT * FROM bus_data", conn)
df.to_csv('./data/bus_data.csv', index=False)