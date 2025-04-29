import asyncio
import os
import logging
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

from async_data_collector import AsyncDataCollector
from async_database_manager import AsyncDatabaseManager

# ✅ 로그 설정
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/data_collector.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def wait_until(hour, minute):
    now = datetime.now()
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if now > target:
        target += timedelta(days=1)
    wait_seconds = (target - now).total_seconds()
    print(f"⏳ {wait_seconds // 60:.0f}분 대기 후 수집 시작...")
    time.sleep(wait_seconds)

async def main():
    # 환경 변수 로딩
    load_dotenv()
    api_keys = os.getenv("API_KEY").split(",")
    dsn = os.getenv("DB_URL")

    resource_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources")
    database_manager = AsyncDatabaseManager(dsn)

    key_index = 0

    # ✅ 5시 30분까지 대기
    wait_until(5, 30)
    print("🚀 수집 시작!")
    start_time = datetime.now()

    while datetime.now() < start_time.replace(hour=10, minute=30):
        start_loop = time.time()
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
                    print(f"✅ 데이터 수집 성공. DB 저장 중...")
                    await database_manager.save_data(buses)
                    print(f"✅ {total_buses}건 저장 완료")
                    logging.info(f"✅ 수집 성공 - 키: {current_key}, 노선 수: {total_routes}, 저장 건수: {total_buses}")
                else:
                    print(f"⚠️ 수집된 데이터 없음")
                    logging.warning(f"⚠️ 수집된 데이터 없음 - 키: {current_key}, 노선 수: {total_routes}")

                success = True
                break

            except Exception as e:
                print(f"🚨 API 키 실패 → 다음 키 시도: {e}")
                logging.error(f"🚨 API 키 실패: {e}")

        if not success:
            print("❌ 모든 API 키 시도 실패. 다음 루프까지 대기...")
            logging.error("❌ 모든 API 키 시도 실패")

        elapsed = time.time() - start_loop
        print(f"🕒 총 소요 시간: {elapsed:.2f}초\n")
        logging.info(f"🕒 총 수집 소요 시간: {elapsed:.2f}초\n")

        await asyncio.sleep(60)

    print("✅ 10시 30분 도달. 수집 종료!")
    logging.info("✅ 10시 30분 도달. 수집 종료!")

if __name__ == "__main__":
    asyncio.run(main())