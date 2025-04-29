import aiohttp
import asyncio
import xmljson
from xml.etree import ElementTree as ET
from datetime import datetime
import pytz
import json
import logging


class AsyncDataCollector:
    def __init__(self, base_url, resources_path):
        self.base_url = base_url  # API 호출을 위한 base URL (route_id가 format으로 삽입됨)
        self.resources_path = resources_path  # JSON 리소스 파일들이 있는 경로
        self.kst_zone = pytz.timezone('Asia/Seoul')  # 한국 시간대 설정
        self.session = aiohttp.ClientSession()  # aiohttp 세션 객체 생성
        
        # 정류장 ID -> 이름 매핑 데이터 로드
        with open(f"{self.resources_path}/station.json", "r", encoding="utf-8") as f:
            self.station_map = json.load(f)

        # 수집 대상 노선 리스트 (route_id, route_name 쌍)
        with open(f"{self.resources_path}/crawlering_route_ids.json", "r", encoding="utf-8") as f:
            self.route_ids = json.load(f)

    async def fetch_data(self, route_id, route_name):
        buses = []
        url = self.base_url.format(route_id)
        try:
            async with self.session.get(url) as response:
                xml_str = await response.text()

                # XML 응답 검증
                if not xml_str.strip().startswith("<?xml"):
                    logging.error(f"⚠️ 잘못된 XML 응답 - route_id={route_id}, 응답: {xml_str[:100]}")
                    return buses  # 빈 리스트 반환해서 collect_data()가 무시하게 됨

                # XML → JSON 파싱
                xml_element = ET.fromstring(xml_str)
                json_data = xmljson.parker.data(xml_element)

                if 'msgBody' not in json_data or 'busLocationList' not in json_data['msgBody']:
                    logging.warning(f"No busLocationList found in the response for route_id {route_id}")
                    return buses

                bus_locations = json_data["msgBody"]["busLocationList"]

                if not isinstance(bus_locations, list):
                    logging.error(f"Unexpected busLocationList type for route_id {route_id}: {type(bus_locations)}")
                    return buses

                if json_data["msgHeader"]["resultCode"] != 0:
                    logging.warning(f"API resultCode is not 0 for route_id {route_id}")
                    return buses

                # 유효한 응답이면 파싱 시작
                time_str = datetime.now(pytz.utc).astimezone(self.kst_zone).strftime("%Y-%m-%d %H:%M:%S")
                time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")

                for data in bus_locations:
                    buses.append({
                        "time": time,
                        "plate_no": data.get("plateNo"),
                        "remain_seat_cnt": data.get("remainSeatCnt", -1),
                        "route_id": route_id,
                        "route_name": route_name,
                        "station_id": str(data.get("stationId")),
                        "station_name": self.station_map.get(str(data.get("stationId")), "Unknown Station"),
                        "station_seq": data.get("stationSeq")
                    })

        except Exception as e:
            logging.error(f"🚨 fetch_data() 예외: route_id={route_id}, error={e}")

        return buses

    async def collect_data(self):
        # 모든 노선 ID에 대해 데이터 수집 작업을 비동기적으로 실행
        tasks = [self.fetch_data(route_id, route_name) for route_id, route_name in self.route_ids]
        results = await asyncio.gather(*tasks)  # 병렬로 결과 수집

        # 결과 평탄화(flatten) 및 빈 값 제외
        buses = [bus for result in results for bus in result if result]
        return buses
    
    async def open(self):
        # 세션이 없을 경우 새로 생성
        if not self.session:
            self.session = await aiohttp.ClientSession()

    async def close(self):
        # 세션 종료
        await self.session.close()