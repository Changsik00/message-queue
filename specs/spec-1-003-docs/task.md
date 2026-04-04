# Task: 1-003 - 아키텍처 구조 문서화 (Docs)

> 이 문서는 구현을 위한 워크로드입니다.
> **문서화 단계(Phase A)** 에서 이 문서가 확정되고 사용자의 승인이 떨어지면, **코딩 단계(Phase B)** 로 넘어갑니다.

## 1. 사전 준비 (Setup)
- [ ] 브랜치 생성 완료 (`git checkout -b spec-1-003/docs`)
- [ ] `docs/architecture` 디렉토리 확립

## 2. 문서화 작업 (Documentation)
- [ ] `docs/architecture/overview.md` 작성 (아키텍처 및 MQ 로직 구성도)
- [ ] `docs/architecture/infrastructure.md` 작성 (Docker 컴포즈 업 필수 조건 및 각 API 서버 실행 가이드 & 포트 테이블)
- [ ] `docs/architecture/mq-comparison.md` 작성 (**4종 MQ 기술 비교 및 서비스별 설계 근거 가이드**)
- [ ] `docs/architecture/event-schema.md` 작성 (이벤트 발행 정보)
- [ ] `README.md`에 아키텍처 문서 링크 맵핑

## 3. 리뷰 및 마무리 (Review & Wrap-up)
- [ ] Markdown 린팅 및 검수 로컬 확인
- [ ] `walkthrough.md` 내용 정리 (해당 Spec 폴더 내)
- [ ] `pr_description.md` 작성
- [ ] PR 반영 및 생성 (`gh pr create`)
