# Agent Kickoff Instructions

> AI Agent는 새로운 대화 도중이나 새로운 작업을 시작할 때 항상 이 문서를 가장 먼저 상기해야 합니다.

## 1. 시작 및 파악 프로세스 (Context Initialization)
1. **현재 스펙 확인**: 사용자가 제시한 작업이 어떤 스펙(`spec-XXX`)에 해당하는지 확인합니다.
2. **디렉토리 정찰**: `/specs/spec-XXX/` 디렉토리가 존재하는지, 그 안의 `spec.md`, `plan.md`, `task.md`, `walkthrough.md` 최신 상태를 확인(`view_file` 도구 사용)합니다.
3. **템플릿 사용**: 만약 `spec.md`나 관련 파일이 없다면, `/.agent/templates/` 디렉토리의 템플릿을 복사하여 `/specs/spec-XXX/` 디렉토리 하위에 먼저 생성하고 사용자의 승인을 받습니다.

## 2. 브랜치 전략 (Git Workflow)
- **절대 메인 브랜치에서 직접 작업하지 않습니다.**
- 현재 브랜치가 `spec-XXX/short-description` 형태인지 확인합니다.
- 아니라면 제일 먼저 아래 명령어로 브랜치를 생성하고 이동합니다.
  ```bash
  git checkout -b spec-{스펙번호}/{짧은_설명}
  ```

## 3. 작업 진행
- **항상 `.agent/constitution.md` 문서의 헌법(절대 규칙)을 준수하며 작업합니다.**
- 작업의 세부 목록은 `specs/spec-XXX/task.md`의 체크박스(`[ ]`)를 기준으로 상태를 전환(`[/]`, `[x]`)하며 진행합니다.