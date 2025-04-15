## ✅ 프로젝트 전체 진행 현황

| 단계 | 내용 | 진행 상태 | 비고 |
|------|------|-----------|------|
| 1️⃣ 가상환경 생성 | `venv`로 Python 가상환경 구성 | ✅ 완료 | `python -m venv venv`로 성공 |
| 2️⃣ 패키지 설치 | 필요 패키지 수동 설치 (aiohttp, asyncpg 등) | ✅ 완료 | 일부는 실행하면서 확인 예정 |
| 3️⃣ 주요 코드 구성 | `main.py`, `collector`, `DB manager` 완성 | ✅ 완료 | 레퍼런스 기반으로 구조화 완료 |
| 4️⃣ API 테스트 | 버스 위치정보 API 호출 테스트 | ✅ 성공 | 인증키 및 URL 문제 해결 |
| 5️⃣ `.env` 구성 | 환경변수 적용 | ✅ 완료 | API key + DB URL 구조 이해 |
| 6️⃣ 데이터 크롤링 로직 | 비동기 방식 구현 완료 | ✅ 완료 | `AsyncDataCollector`로 구조화 |
| 7️⃣ DB 연동 준비 | 아직 TimescaleDB 미구축 | ⏳ 진행 중 | Docker 다운로드 중 |
| 8️⃣ DB 테이블 생성 | `initialize_database.py` 실행 예정 | ❌ 미완료 | DB 붙은 후 바로 실행 가능 |
| 9️⃣ 실시간 수집 실행 | `main.py` 통한 주기적 수집 | ❌ 테스트 필요 | DB 연결되면 검증 가능 |
| 🔟 CSV 출력 테스트 | `make_csv_file.py`로 데이터 저장 | ❌ 미완료 | DB 연결되면 추출 가능 |

---

## 🧩 앞으로 해야 할 작업 (우선순위 순)

1. **Docker 설치 완료**  
   → TimescaleDB 띄울 준비

2. **TimescaleDB 컨테이너 실행**  
   → `docker run ...` 명령어로 실행  
   → `.env`의 `DB_URL` 값 설정

3. **초기화 스크립트 실행**  
   → `python initialize_database.py`  
   → 테이블 + 하이퍼테이블 생성 확인

4. **`main.py` 실행 테스트**  
   → 실시간 수집 및 DB 저장 확인  
   → 응답 데이터 수, 저장 로그 확인

5. **CSV로 결과 추출** (선택)  
   → `make_csv_file.py` 실행  
   → 저장된 데이터 확인 및 활용

6. (선택) **모델 학습 파이프라인 설계 시작**  
   → 예측 목적에 맞춘 데이터 전처리/모델 설계 가능

---

## 🧭 지금 상태는?

```text
[환경 구축 및 코드 준비] ▶️ 완료
[DB 세팅] ▶️ 진행 중 (Docker 다운로드 중)
[전체 파이프라인 작동 테스트] ▶️ 아직
```

---

## 크롤러 코드 구조 요약

```
📁 프로젝트 루트
│
├── main.py                      🔁 전체 수집 루프 실행
├── async_data_collector.py     📡 API 요청 + 버스 데이터 수집 (비동기)
├── async_database_manager.py   🗃️ 수집된 데이터 DB에 저장
├── initialize_database.py      🛠️ DB 테이블/하이퍼테이블 생성
├── make_csv_file.py            📄 저장된 DB → CSV 추출 (선택)
│
└── resources/                  📁 리소스 폴더
    ├── crawlering_route_ids.json   🛣️ 수집 대상 노선 리스트
    └── station.json                🚌 정류장 ID ↔ 이름 매핑
```

---

## 🔄 실행 흐름 요약

1. `main.py` 실행  
2. → `AsyncDataCollector`가 각 노선 ID에 대해 API 요청  
3. → 응답받은 버스 위치 + 잔여좌석 데이터 파싱  
4. → `AsyncDatabaseManager`가 `bus_data` 테이블에 저장  
5. → 1분 주기로 반복 수집

---

## ⚙️ 핵심 구성 요소 요약

| 파일명 | 역할 |
|--------|------|
| `main.py` | 크롤러 전체 루프 제어 |
| `async_data_collector.py` | 비동기 API 요청, 응답 파싱, 시간 처리 |
| `async_database_manager.py` | asyncpg를 사용한 비동기 DB 저장 |
| `initialize_database.py` | `bus_data` 테이블 + 하이퍼테이블 생성 |
| `resources/*.json` | 노선 리스트와 정류장 정보 매핑 파일 |
