import pandas as pd
import psycopg2
from dotenv import load_dotenv
import os

# .env 불러오기
load_dotenv()
dsn = os.getenv("DB_URL")

# 연결
conn = psycopg2.connect(dsn)

# 전체 데이터 로드
df = pd.read_sql_query("SELECT * FROM bus_data ORDER BY time", conn)

# 상위 8개 샘플 데이터 제거
df = df.iloc[8:]

# CSV 저장
df.to_csv('./data/bus_data.csv', index=False)
print(f"✅ {len(df)}건을 저장했습니다.")
