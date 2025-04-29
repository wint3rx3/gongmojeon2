import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv
import os

def create_tables(cursor):
    # bus_data 테이블이 존재하면 삭제
    cursor.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'bus_data'
            ) THEN
                DROP TABLE bus_data CASCADE;
            END IF;
        END
        $$;
    """)

    # bus_data 테이블 생성 (시간 시계열, 버스 정보 저장용)
    cursor.execute("""
        CREATE TABLE bus_data (
            time TIMESTAMPTZ NOT NULL,          -- 수집 시각 (시간대 포함)
            plate_no TEXT,                      -- 버스 번호판
            route_id TEXT,                      -- 노선 ID
            route_name TEXT,                    -- 노선 이름
            remain_seat_cnt INTEGER,            -- 잔여 좌석 수
            station_id TEXT,                    -- 정류장 ID
            station_name TEXT,                  -- 정류장 이름
            station_seq INTEGER                 -- 정류장 순번
        );
    """)

def create_hypertable(cursor):
    # TimescaleDB 하이퍼테이블 생성 (기존에 존재하면 무시)
    cursor.execute("SELECT create_hypertable('bus_data', 'time', if_not_exists => TRUE);")

def insert_test(cursor, conn):
    # 테스트용 데이터 리스트
    buses = [
        ("2024-03-22 00:14:48","경기73아1737","219000013","1000",43,"219000340","양우아파트",1),
        ("2024-03-22 00:14:49","경기73아1737","219000013","1000",42,"219000341","양우아파트",2),
        ("2024-03-22 00:15:48","경기73아1737","219000013","1000",39,"219000342","양우아파트",3),
        ("2024-03-22 00:15:49","경기73아1737","219000013","1000",38,"219000345","양우아파트",4),
        ("2024-03-22 00:16:48","경기73아1737","219000013","1000",12,"219000349","양우아파트",5),
        ("2024-03-22 00:16:48","경기73아1737","219000013","1000",1,"219000400","양우아파트",6),
        ("2024-03-22 00:18:48","경기73아1737","219000013","1000",0,"219000401","양우아파트",12),
        ("2024-03-22 00:19:48","경기73아1737","219000013","1000",25,"219000403","양우아파트",23),
    ]

    # 버스 데이터 삽입
    for bus in buses:
        try:
            cursor.execute(
                "INSERT INTO bus_data (time, plate_no, route_id, route_name, remain_seat_cnt, station_id, station_name, station_seq) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (bus[0], bus[1], bus[2], bus[3], bus[4], bus[5], bus[6], bus[7])
            )
        except (Exception, psycopg2.Error) as error:
            print(error.pgerror)  # 에러 발생 시 출력
    conn.commit()  # 커밋
    cursor.close()  # 커서 종료

def main():
    load_dotenv()  # .env 파일에서 환경변수 로드
    dsn = os.getenv("DB_URL")  # DB 연결 문자열 가져오기
    conn = psycopg2.connect(dsn)  # PostgreSQL 연결
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)  # 자동 커밋 설정 
    
    with conn.cursor() as cursor:
        create_tables(cursor)         # 테이블 생성 (있으면 삭제 후 생성)
        create_hypertable(cursor)     # 하이퍼테이블로 변환
        insert_test(cursor, conn)     # 테스트용 데이터 삽입
        
    conn.close()  # 연결 종료
    print("✅ DB 초기화 완료")  # 완료 메시지

if __name__ == "__main__":
    main()  # 메인 함수 실행
