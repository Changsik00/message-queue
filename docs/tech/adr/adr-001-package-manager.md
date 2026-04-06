# ADR-001: Node.js 패키지 매니저 및 버전 고정 전략

## 상태
**Accepted**

## 배경
기존에는 `npm`을 사용하고 프로젝트별로 상이한 `package-lock.json`이 관리되었습니다. 또한 의존성 버전이 `^` 등으로 느슨하게 지정되어 있어 개발 환경 간의 불일치 발생 가능성이 높았습니다.

## 결정
1.  **pnpm 도입**: 설치 속도 향상 및 디스크 공간 절약을 위해 pnpm을 사용합니다.
2.  **Corepack 활성화**: `package.json`의 `packageManager` 필드를 명시하고 Corepack을 통해 버전을 강제합니다.
3.  **버전 고정**: 모든 `package.json`에서 `^`, `~`를 제거하고 고정 버전(Fixed Versions)을 사용하여 환경 일관성을 확보합니다.

## 결과 및 향후 계획
- **결과**: `pnpm-lock.yaml`을 통한 재현 가능한 빌드 환경 구축.
- **향후 계획**: Phase 3 단계 진입 전 `pnpm workspace` 구성을 완료하여 공통 라이브러리 관리를 효율화할 예정입니다.
