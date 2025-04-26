import asyncio
import os
import time
from dotenv import load_dotenv

from async_data_collector import AsyncDataCollector
from async_database_manager import AsyncDatabaseManager


async def main():
    # 환경 변수 로딩
    load_dotenv()
    api_key = os.getenv("GBUS_API_KEY")
    dsn = os.getenv("DB_URL")

    # 요청 URL 템플릿 설정 (v2 JSON 응답용)
    base_url = f"http://apis.data.go.kr/6410000/buslocationservice/v2/getBusLocationListv2?serviceKey={api_key}&routeId={{}}&format=xml"

    # 리소스 경로 (노선 목록 json 등)
    resource_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources")

    # 수집기, DB 매니저 준비
    data_collector = AsyncDataCollector(base_url, resource_path)
    data_collector.route_ids = data_collector.route_ids[:5]
    database_manager = AsyncDatabaseManager(dsn)

    # aiohttp 세션 열기
    await data_collector.open()

    for _ in range(2):  # 2바퀴만 반복
        start_time = time.time()

        # 데이터 수집
        buses = await data_collector.collect_data()

        if buses:
            print("✅ 데이터 수집 완료. DB 저장 중...")
            await database_manager.save_data(buses)
            print(f"✅ {len(buses)}건 저장 완료")
        else:
            print("⚠️ 수집된 데이터 없음")

        elapsed = time.time() - start_time
        print(f"🕒 총 소요 시간: {elapsed:.2f}초\n")

        await asyncio.sleep(60)

    await data_collector.close()


if __name__ == "__main__":
    asyncio.run(main())
