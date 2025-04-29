import asyncio
import os
import logging
import time
from datetime import datetime
from dotenv import load_dotenv

from async_data_collector import AsyncDataCollector
from async_database_manager import AsyncDatabaseManager

# 로그 설정
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/data_collector.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8"
)

async def main():
    load_dotenv()
    api_keys = os.getenv("API_KEY").split(",")
    dsn = os.getenv("DB_URL")

    resource_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources")
    database_manager = AsyncDatabaseManager(dsn)

    key_index = 0

    while True:
        loop_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        start_time = time.time()
        success = False

        for attempt in range(len(api_keys)):
            current_key = api_keys[key_index % len(api_keys)]
            key_index += 1

            base_url = f"http://apis.data.go.kr/6410000/buslocationservice/v2/getBusLocationListv2?serviceKey={current_key}&routeId={{}}&format=xml"

            try:
                data_collector = AsyncDataCollector(base_url, resource_path)
                await data_collector.open()
                buses = await data_collector.collect_data()

                total_routes = len(data_collector.route_ids)
                total_buses = len(buses)

                if buses:
                    await database_manager.save_data(buses)
                    print(f"[{loop_time}] 수집 성공 - 노선 수: {total_routes}, 저장 건수: {total_buses}")
                    logging.info(f"[{loop_time}] 수집 성공 - 노선 수: {total_routes}, 저장 건수: {total_buses}")
                else:
                    print(f"[{loop_time}] 수집된 데이터 없음")
                    logging.warning(f"수집된 데이터 없음 - 노선 수: {total_routes}")

                success = True
                break

            except Exception as e:
                print(f"[{loop_time}] API 키 실패 → 다음 키 시도")
                logging.error(f"API 키 실패: {e}")

        if not success:
            print(f"[{loop_time}] 모든 API 키 시도 실패. 다음 루프까지 대기...")
            logging.error("모든 API 키 시도 실패")

        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())