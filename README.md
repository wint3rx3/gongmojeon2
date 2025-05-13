## 🗂️ 파일 디렉토리 구조
```
project_root/
├── data/
│   └── bus_data.csv                   # 수집된 버스 정보 데이터를 저장한 CSV 파일
├── logs/
│   └── data_collector.log            # 데이터 수집 실행 중 발생한 로그 기록
├── resources/
│   ├── all_route_ids.json            # 모든 버스 노선 ID 정보
│   ├── crawlering_route_ids.json     # 수집 대상 버스 노선 ID 목록
│   └── station.json                  # 버스 정류장 관련 메타데이터
├── venv/                             # Python 가상환경 디렉토리 (보통 Git에서 제외)
├── .env                              # API 키 등 환경변수 설정 파일
├── async_data_collector.py           # 비동기 방식으로 버스 데이터를 수집하는 모듈
├── async_database_manager.py         # 비동기 데이터베이스 입출력 처리 모듈
├── initialize_database.py            # 데이터베이스 초기화 및 테이블 생성 스크립트
├── main_test.py                      # 테스트용 실행 파일 (기능별 모듈 검증 목적)
├── main_timer.py                     # 일정 주기로 데이터 수집을 수행하는 메인 실행 파일
├── make_csv.py                       # 수집된 데이터를 CSV 형식으로 변환 및 저장하는 스크립트
├── README.md                         # 프로젝트 소개 및 실행 방법 설명 문서
├── requirements.txt                  # 필요한 Python 패키지 목록
```

## ⚡ 퀵 스타트
### 1. Python 가상환경 설정 (venv)
가상환경 생성

```bash
python -m venv venv
```
가상환경 활성화

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 실행
# Windows
.\venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```
이미 가상환경 세팅을 끝냈다면,
```
.\venv\Scripts\activate
```

### 2. 필요한 라이브러리 설치
아래 명령어로 모든 라이브러리를 설치

```bash
pip install -r requirements.txt
```

### 3. Docker로 TimescaleDB 실행
설치 후, 터미널에서 Docker가 잘 작동하는지 확인
```
docker --version
```
정상적으로 설치되었다면 버전 정보가 출력됩니다.

```bash
docker run -d \
  --name timescaledb \
  -p 5432:5432 \
  -e POSTGRES_PASSWORD=your_password \
  -e POSTGRES_DB=your_db_name \
  timescale/timescaledb:latest-pg15
```
- your_password, your_db_name은 자유롭게 설정하세요.
- 이 정보는 .env 파일에도 아래와 같이 동일하게 등록해야 합니다.
```
DB_URL=postgresql://postgres:your_password@localhost:5432/your_db_name
```


### 4. API 키 발급 및 설정
경기도 버스정보 API (GBIS) 접속

API 신청 후, .env 파일에 다음처럼 추가

```ini
API_KEY=여기에_발급받은_API_KEY
```

### 5. DB 초기화
아래 명령어 실행

```bash
python initialize_database.py
```
초기화 내용:
- 기존 bus_data 테이블 삭제
- 새로 생성 (TimescaleDB 하이퍼테이블 적용)
- 테스트용 샘플 데이터 삽입

### 6. 데이터 수집 테스트
테스트 코드 (main_copy.py)

```bash
python main_test.py
```
출퇴근 시간 자동 크롤링 설정 (main.py)

```bash
python main_timer.py
```

### 7. 수집된 데이터 확인
CSV 저장 (DB → 파일)

```bash
python make_csv.py
```
