import pandas as pd
import psycopg2
from dotenv import load_dotenv
import os

# .env 불러오기
load_dotenv()
dsn = os.getenv("DB_URL")  # 예: postgresql://user:pw@localhost:5432/dbname

# 연결
conn = psycopg2.connect(dsn)

# 쿼리 → DataFrame → CSV 저장
df = pd.read_sql_query("SELECT * FROM bus_data", conn)
df.to_csv('./datas/bus_data2.csv', index=False)