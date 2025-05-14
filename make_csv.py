import pandas as pd
import psycopg2
from dotenv import load_dotenv
import os
from datetime import datetime

# 환경변수 로드
load_dotenv()
dsn = os.getenv("DB_URL")

# DB 연결
conn = psycopg2.connect(dsn)

# 데이터 불러오기
df = pd.read_sql_query("SELECT * FROM bus_data ORDER BY time", conn)

# 상위 8개 제거
df = df.iloc[8:]

# 오늘 날짜 포맷 지정
today_str = datetime.now().strftime("%Y%m%d")

# CSV 저장 경로 생성
csv_path = f'./data/bus_data_{today_str}.csv'
df.to_csv(csv_path, index=False)

print(f"💾 {len(df)}건을 저장했습니다: {csv_path}")
