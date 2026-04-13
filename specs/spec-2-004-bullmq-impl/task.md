# Task: 2-004 - BullMQ 구현 (BullMQ MVP)

> 이 문서는 구현을 위한 워크로드입니다.
> **문서화 단계(Phase A)** 에서 이 문서가 확정되고 사용자의 승인이 떨어지면, **코딩 단계(Phase B)** 로 넘어갑니다.
> 코딩 단계 진입 후에는 **사용자의 허락을 구하지 말고 자율적으로 끝까지 진행**하며, `[ ]` 항목 하나를 `[x]`로 완료할 때마다 **반드시 1번의 git commit**을 수행하세요.

## 1. 사전 준비 (Setup)
- [ ] 브랜치 생성 (`git checkout -b spec-2-004/bullmq-impl`)
- [ ] Node.js 의존성 추가 (`bullmq`, `@bull-board/api`, `@bull-board/express`, `express`, `@types/express` → `workers/node/package.json`, `pnpm install`)
- [ ] Python 의존성 추가 (`rq`, `redis` → `workers/python/requirements.txt`, `api-server/python/requirements.txt`)

## 2. Producer 구현 (API Server)
- [ ] `api-server/python/main.py` — `BullMQQueue` 클래스 구현 및 `POST /bullmq/orders` 엔드포인트 추가
  - `redis-py` 로 BullMQ Redis 키 구조(`bull:orders:*`)에 직접 Job enqueue
  - `rq` 로 `orders-python` 큐에도 동시 enqueue

## 3. Node.js Worker 구현 (BullMQ)
- [ ] `workers/node/src/bullmq.worker.ts` 파일 생성
  - `bullmq` 의 `Worker` 클래스로 `orders` 큐 구독 (`concurrency: 1`)
  - `attempts: 3`, `backoff: { type: 'exponential', delay: 1000 }` 재시도 설정
  - `SIMULATE_FAILURE` 환경변수 기반 50% 강제 실패 로직
  - 정상 처리 시 `processed_events` DB 저장 (`mq_type='bullmq'`, `group_id='inventory-group'`)
  - Bull Board Express 서버 내장 (`:3001/ui`)

## 4. Python Worker 구현 (RQ)
- [ ] `workers/python/bullmq_worker.py` 파일 생성
  - `rq` 의 `Worker` 클래스로 `orders-python` 큐 구독
  - `SIMULATE_FAILURE` 환경변수 기반 50% 강제 실패 로직
  - 정상 처리 시 `processed_events` DB 저장 (`mq_type='bullmq'`, `group_id='payment-group'`)

## 5. 통합 및 검증 (Integration & Verification)
- [ ] `docker compose up postgres redis -d` 로 인프라 기동 확인
- [ ] BullMQ Worker, RQ Worker 동시 실행 후 `POST /bullmq/orders` 5회 호출
- [ ] DB에서 `mq_type='bullmq'` 레코드 조회 — inventory 5개 + payment 5개 총 10개 확인
- [ ] Bull Board UI(`http://localhost:3001/ui`) 접속 → Job `completed` 상태 확인
- [ ] `SIMULATE_FAILURE=true` BullMQ Worker 실행 후 메시지 발행 → Bull Board에서 `failed` 상태 + 재시도 횟수 확인

## 6. 리뷰 및 마무리 (Review & Wrap-up)
- [ ] 개발된 내용이 정상 동작하는지 Agent 차원의 자체 로컬 테스트 및 검증 (필수)
- [ ] 전체 기능 동작 확인 및 린팅(Linting) / 포맷팅(Formatting)
- [ ] `walkthrough.md` 작성 (아키텍처 다이어그램, 검증 결과 포함)
- [ ] `pr_description.md` 파일 작성
- [ ] `git push` 후, `gh pr create --title ... --body-file pr_description.md` 로 PR 생성
