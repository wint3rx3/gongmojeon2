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
GBUS_API_KEY=여기에_발급받은_API_KEY
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
크롤링 테스트를 위한 설정 (main_copy.py)

```bash
python main_copy.py
```
전체 버전 실행 (main.py)

```bash
python main.py
```

### 7. 수집된 데이터 확인
CSV 저장 (DB → 파일)

```bash
python make_csv.py
```
