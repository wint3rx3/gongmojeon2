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
        with open(f"{self.resources_path}/station.json", "r") as f:
            self.station_map = json.load(f)

        # 수집 대상 노선 리스트 (route_id, route_name 쌍)
        with open(f"{self.resources_path}/crawlering_route_ids.json", "r") as f:
            self.route_ids = json.load(f)

    async def fetch_data(self, route_id, route_name):
        buses = []
        url = self.base_url.format(route_id)  # 해당 노선의 API URL 생성
        async with self.session.get(url) as response:
            xml_str = await response.text()  # 응답을 문자열(XML)로 읽기
            xml_element = ET.fromstring(xml_str)  # XML 파싱
            json_data = xmljson.parker.data(xml_element)  # XML → JSON 형태로 변환

            # 응답 본문 또는 위치 목록이 없는 경우 예외 처리
            if 'msgBody' not in json_data or 'busLocationList' not in json_data['msgBody']:
                logging.warning(f"No busLocationList found in the response for route_id {route_id}")
                return buses
            
            bus_locations = json_data["msgBody"]["busLocationList"]

            # 단일 객체인 경우 예외 처리
            if not isinstance(bus_locations, list):
                logging.error(f"Unexpected busLocationList type for route_id {route_id}: {type(bus_locations)}")
                return buses
            
            # 응답 코드가 0이 아니면 무효 처리
            if json_data["msgHeader"]["resultCode"] != 0:
                logging.warning(f"Request ignored or result is unexpected: {json_data}")
                return buses

            # 각 버스 정보를 순회하며 필요한 항목 추출
            for data in bus_locations:
                # 현재 시간 기준으로 타임스탬프 생성 (한국 시간)
                time_str = datetime.now(pytz.utc).astimezone(self.kst_zone).strftime("%Y-%m-%d %H:%M:%S")
                time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")

                # 버스 정보 파싱
                plate_no = data.get("plateNo")  # 차량 번호
                plate_type = data.get("plateType")  # 차량 종류 (사용하지 않음)
                remain_seat_cnt = data.get("remainSeatCnt", -1)  # 잔여 좌석 수
                station_id = str(data.get("stationId"))  # 정류장 ID
                station_name = self.station_map.get(str(station_id), "Unknown Station")  # 정류장 이름
                station_seq = data.get("stationSeq")  # 정류장 순번
                
                # 하나의 버스 데이터를 딕셔너리로 저장
                buses.append({
                    "time": time,
                    "plate_no": plate_no,
                    "remain_seat_cnt": remain_seat_cnt,
                    "route_id": route_id,
                    "route_name": route_name,
                    "station_id": station_id,
                    "station_name": station_name,
                    "station_seq": station_seq
                })

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
