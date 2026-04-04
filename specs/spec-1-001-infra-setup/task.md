# Task: 1-001 - 인프라 기반 구축 (Infra MVP)

> 이 문서는 구현을 위한 워크로드입니다.
> **문서화 단계(Phase A)** 에서 이 문서가 확정되고 사용자의 승인이 떨어지면, **코딩 단계(Phase B)** 로 넘어갑니다.
> 코딩 단계 진입 후에는 **사용자의 허락을 구하지 말고 자율적으로 끝까지 진행**하며, `[ ]` 항목 하나를 `[x]`로 완료할 때마다 **반드시 1번의 git commit**을 수행하세요.

## 1. 사전 준비 (Setup)
- [x] 브랜치 생성 완료 (`git checkout -b spec-1-001/infra-setup`)

## 2. 세부 구현 (Implementation)
- [x] `db/init.sql` 파일 생성 (DDL 작성 - `orders`, `event_logs` 테이블)
- [x] `docker-compose.yml` 파일 작성 (Service 5개 할당: Kafka, RabbitMQ, Redis, Mosquitto, PostgreSQL)
- [x] `docker-compose.yml` 컨테이너 내 헬스체크 구문 추가 및 `init.sql` 파일 마운트 볼륨 바인딩 처리

## 3. 통합 및 검증 (Integration & Verification)
- [x] 터미널에서 `docker compose up -d` 명령어 구동 및 컨테이너 로그 및 `healthy` 확인 (에이전트가 직접 수행하여 검증 완료)
- [x] `psql` 또는 컨테이너 exec 기능을 통해 데이터베이스 내 테이블 생성이 정상적으로 이뤄졌는지 검증
- [x] `docker compose down` 명령어로 볼륨/구동 잔여물 클린 체크

## 4. 리뷰 및 마무리 (Review & Wrap-up)
- [x] 작성된 파일 린팅(Yaml 포맷 등) / 최종 코드 검토
- [x] `walkthrough.md` 파일 초안 작성 추가 
- [x] **최종 기능 병합을 위한 PR(Pull Request) 생성 및 승인 요청 (`pr.md` 활용)**
