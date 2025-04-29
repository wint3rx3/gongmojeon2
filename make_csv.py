import pandas as pd
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()
dsn = os.getenv("DB_URL")

conn = psycopg2.connect(dsn)

# 데이터 불러오기
df = pd.read_sql_query("SELECT * FROM bus_data ORDER BY time", conn)

# 상위 8개 제거
df = df.iloc[8:]

# CSV 저장 
df.to_csv('./data/bus_data.csv', index=False)
print(f"💾 {len(df)}건을 저장했습니다.")
