# Task: 1-002 - 애플리케이션 코어 및 공통 인터페이스 설계 (Core MVP)

> 이 문서는 구현을 위한 워크로드입니다.
> **문서화 단계(Phase A)** 에서 이 문서가 확정되고 사용자의 승인이 떨어지면, **코딩 단계(Phase B)** 로 넘어갑니다.
> 코딩 단계 진입 후에는 **사용자의 허락을 구하지 말고 자율적으로 끝까지 진행**하며, `[ ]` 항목 하나를 `[x]`로 완료할 때마다 **반드시 1번의 git commit**을 수행하세요.

## 1. 사전 준비 (Setup & TDD Draft)
- [x] 브랜치 생성 완료 (`git checkout -b spec-1-002/core-mvp`)
- [x] Python, Node.js 기본 프로젝트 구조 스캐폴딩 설정 (`requirements.txt`, `package.json` 등 기초 파일)

## 2. 세부 구현 (Implementation)
- [x] `workers/python/base_queue.py`: `OrderEvent` 모델(`publishedAt` 포함) 및 `BaseQueue` 인터페이스 정의
- [x] `workers/node/src/base-queue.interface.ts`: `OrderEvent` 인터페이스 및 `BaseQueue` 인터페이스 정의
- [x] `api-server/python/main.py`: FastAPI 초기화 및 `POST /orders` 라우트 생성 (Mock 큐 연결)
- [x] `api-server/node/src/main.ts`: Express 초기화 및 `POST /orders` 라우트 생성 (Mock 큐 연결)

## 3. 통합 및 검증 (Integration & Verification)
- [x] Python 서버 구동(`uvicorn`) 및 cURL 테스트 통과 (`POST /orders`)
- [x] Node 서버 구동 및 cURL 테스트 통과 (`POST /orders`)

## 4. 리뷰 및 마무리 (Review & Wrap-up)
- [x] 단위 검증 및 코드 포맷팅
- [x] `walkthrough.md` 작성 및 아키텍처 다이어그램 업데이트
- [x] `pr_description.md` 생성
- [x] 리모트에 브랜치 푸시 후 `gh pr create` 명령어로 PR 작성 및 보고
