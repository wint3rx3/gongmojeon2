좋아요! 이 디렉토리 구조를 기준으로, 팀원에게 공유하기 좋은 형태의 **"프로젝트 파일 설명 문서"**를 아래와 같이 정리해볼게요.  
각 파일/폴더가 어떤 역할을 하고, 내부의 주요 함수들은 어떤 기능을 하는지를 중심으로 구성했어요.

---

# 📁 프로젝트 구조 및 파일 설명서

이 프로젝트는 **경기도 광역버스의 실시간 잔여 좌석 데이터를 수집하고, DB에 저장하여 분석 및 예측에 활용**하기 위한 비동기 크롤러 시스템입니다.

---

## 📂 resources/  
API 호출 시 필요한 리소스(JSON)들을 담은 폴더입니다.

### ▸ `crawlering_route_ids.json`
- 수집 대상 `route_id`와 `route_name`을 리스트 형태로 정의한 파일
- 예: `[["233000031", "9302"], ["219000026", "9700"]]`
- `AsyncDataCollector`에서 이 파일을 참조하여 반복적으로 크롤링을 수행합니다.

### ▸ `station.json`
- 정류장 ID → 정류장 이름 매핑 정보
- API 응답에서 받은 정류장 ID를 사람이 알아보기 쉽게 이름으로 바꾸기 위해 사용됩니다.

---

## 📂 utils/  
보조 기능 유틸리티 코드가 위치한 폴더입니다.

### ▸ `make_csv_file.py`
- 목적: **DB에 저장된 수집 데이터를 CSV 파일로 export**
- 주 용도:
  - 모델 학습 전 데이터 추출
  - 분석용 데이터 저장
- 주요 함수:
  - 없음 (단일 실행 스크립트 형태로, 실행 시 전체 데이터 CSV로 저장)

---

## 📄 .env  
- 환경변수 파일 (절대 Git에 올리지 말 것!)
- 예시 키:
  - `GBUS_API_KEY` : 경기버스 정보 Open API 인증키
  - `DB_URL` : PostgreSQL/TimescaleDB 접속 URL

---

## 📄 async_data_collector.py  
- 비동기로 API를 호출해 **버스의 위치 및 좌석 정보를 수집하는 핵심 로직**
- 주요 클래스: `AsyncDataCollector`

### 주요 메서드
- `fetch_data(route_id, route_name)`  
  : 단일 노선 ID에 대한 API 요청 및 결과 파싱  
- `collect_data()`  
  : 전체 노선 리스트에 대해 병렬로 `fetch_data` 수행  
- `open()` / `close()`  
  : `aiohttp.ClientSession` 열기/닫기

---

## 📄 async_database_manager.py  
- 수집된 데이터를 PostgreSQL/TimescaleDB에 저장하는 모듈
- 주요 클래스: `AsyncDatabaseManager`

### 주요 메서드
- `connect()` : DB 연결 (필요할 때만 실행)
- `save_data(buses)` : 수집된 버스 리스트를 `bus_data` 테이블에 일괄 저장
- `close()` : DB 연결 종료

---

## 📄 initialize_database.py  
- DB에 필요한 테이블 및 TimescaleDB의 하이퍼테이블을 **초기 1회 생성**하는 스크립트

### 주요 함수
- `create_tables()` : `bus_data` 테이블 생성
- `create_hypertable()` : TimescaleDB 하이퍼테이블로 등록
- `insert_test()` : 테스트 데이터 삽입 (선택 사항)

📌 **`main.py` 실행 전에 한 번만 실행해주면 됩니다.**

---

## 📄 main.py  
- **실제 크롤러를 주기적으로 실행하는 진입점**
- `AsyncDataCollector`, `AsyncDatabaseManager`를 사용해
  - 실시간으로 API 데이터를 수집하고
  - DB에 저장하며
  - 60초 주기로 반복 실행합니다.

### 핵심 로직
- `.env` 로딩
- `base_url` 구성
- 무한 루프 내에서:
  - `collect_data()` 호출 → `save_data()` 저장 → sleep 60초

---

## 📄 requirements.txt  
- 프로젝트 실행에 필요한 패키지 목록  
- 예시 항목:
  - `aiohttp`
  - `asyncpg`
  - `psycopg2`
  - `python-dotenv`
  - `pandas`

```txt
aiohttp
asyncpg
psycopg2
python-dotenv
pandas
```

---

## ✅ 프로젝트 시작 전 체크리스트

1. `.env` 파일 작성
2. `initialize_database.py` 1회 실행 → 테이블/하이퍼테이블 생성
3. `resources/` 폴더에 JSON 파일 존재 확인
4. `main.py` 실행으로 실시간 수집 시작

---

필요시 이 문서를 `README.md`나 `docs/overview.md`로 저장해서 팀에 공유하면 좋아요!  
또, 향후 시각화, 모델 학습, API 서비스 확장 등으로 넘어가도 **기초 구조가 탄탄**해서 매우 좋습니다 😊
