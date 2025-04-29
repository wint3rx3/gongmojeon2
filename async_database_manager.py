import asyncpg

class AsyncDatabaseManager:
    def __init__(self, dsn):
        self.dsn = dsn  # DB 연결 문자열 (PostgreSQL DSN)
        self.conn = None  # 비동기 커넥션 객체 초기화
    
    async def connect(self):
        # DB 연결이 없거나 닫혀 있는 경우 새로운 연결 생성
        if self.conn is None or self.conn.is_closed():
            self.conn = await asyncpg.connect(self.dsn)

    async def close(self):
        # DB 연결 종료
        await self.conn.close()
        
    async def save_data(self, buses):
        # DB 연결 보장
        await self.connect()
        # 트랜잭션을 열고 데이터를 한번에 삽입
        async with self.conn.transaction():
            await self.conn.executemany("""
                INSERT INTO bus_data (time, plate_no, route_id, route_name, 
                remain_seat_cnt, station_id, station_name, station_seq)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """, [
                    # 수집된 각 버스 데이터를 튜플로 변환
                    (
                        bus['time'],
                        bus['plate_no'],
                        bus['route_id'],
                        bus['route_name'],
                        bus['remain_seat_cnt'],
                        bus['station_id'],
                        bus['station_name'],
                        bus['station_seq']
                    ) for bus in buses
                ])