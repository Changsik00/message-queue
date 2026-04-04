# Task: {SPEC_NUMBER} - {TITLE}

> 이 문서는 구현을 위한 워크로드입니다.
> **문서화 단계(Phase A)** 에서 이 문서가 확정되고 사용자의 승인이 떨어지면, **코딩 단계(Phase B)** 로 넘어갑니다.
> 코딩 단계 진입 후에는 **사용자의 허락을 구하지 말고 자율적으로 끝까지 진행**하며, `[ ]` 항목 하나를 `[x]`로 완료할 때마다 **반드시 1번의 git commit**을 수행하세요.

## 1. 사전 준비 (Setup & TDD Draft)
- [ ] 브랜치 생성 완료 (`git checkout -b spec-XXX/desc`)
- [ ] 테스트 코드 뼈대(Test Stub/Mock) 작성

## 2. 세부 구현 (Implementation)
- [ ] 기능 A 구현
- [ ] 기능 A 단위 테스트 패스
- [ ] 기능 B 구현
- [ ] 기능 B 단위 테스트 패스

## 3. 통합 및 검증 (Integration & Verification)
- [ ] 통합 테스트 (API 호출, DB 연동 등)
- [ ] (선택) 부하 테스트 또는 에지 케이스 검증

## 4. 리뷰 및 마무리 (Review & Wrap-up)
- [ ] 개발된 내용이 정상 동작하는지 Agent 차원의 자체 로컬 테스트 및 검증 (필수)
- [ ] 전체 기능 동작 확인 및 린팅(Linting) / 포맷팅(Formatting)
- [ ] `walkthrough.md` 구조, 에러 로그 및 아키텍처 다이어그램(Mermaid) 최종 점검 및 업데이트
- [ ] `pr_description.md` 파일 작성 (해당 스펙 폴더 내)
- [ ] `git push` 후, 로컬 터미널의 `gh` CLI 명령어를 통해 리포지토리에 실제 PR 생성 (`gh pr create --title ... --body-file pr_description.md`)
