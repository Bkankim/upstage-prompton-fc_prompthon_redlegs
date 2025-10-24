# 문서 가이드

이 디렉토리는 프로젝트의 모든 문서를 포함합니다.

## 문서 구조

### 핵심 문서 (읽기 순서)

1. **[01_GETTING_STARTED.md](./01_GETTING_STARTED.md)** - 시작하기
   - 환경 설정 (uv 설치, 의존성)
   - 빠른 실행 (Baseline 재현)
   - 프로젝트 구조 이해
   - 핵심 명령어

2. **[02_EXPERIMENT_INSIGHTS.md](./02_EXPERIMENT_INSIGHTS.md)** - 실험 인사이트 ⭐ 필독
   - Phase 1-6 실험 여정
   - 주요 실패 사례 및 원인 분석
   - 핵심 발견 5가지
   - 기술적 한계 및 교훈

3. **[03_TECHNICAL_DETAILS.md](./03_TECHNICAL_DETAILS.md)** - 기술 구현 상세
   - 아키텍처 (Generator, Prompt, Evaluator)
   - 평가 지표 (LCS 기반 Recall)
   - 프롬프트 설계 원칙
   - 성능 최적화

4. **[04_COMPETITION_GUIDE.md](./04_COMPETITION_GUIDE.md)** - 대회 정보
   - 대회 개요 및 제약사항
   - 데이터셋 구성 (오류 유형)
   - 평가 방식 (Recall 계산)
   - 제출 형식

### 레거시 문서 (참고용)

아래 문서들은 통합 문서로 대체되었습니다:

#### getting-started/ (→ 01_GETTING_STARTED.md)
- ~~QUICK_START.md~~
- ~~UV_ENVIRONMENT_GUIDE.md~~
- ~~BASELINE_CODE.md~~

#### advanced/ (→ 02_EXPERIMENT_INSIGHTS.md + 03_TECHNICAL_DETAILS.md)
- ~~ADVANCED_STRATEGIES.md~~
- ~~EXPERT_ADVICE_STRATEGY.md~~
- ~~EXPERIMENT_LESSONS.md~~

#### code/ (→ 03_TECHNICAL_DETAILS.md)
- ~~GENERATOR_ARCHITECTURE.md~~
- ~~MIGRATION_GUIDE.md~~

#### competition/ (→ 04_COMPETITION_GUIDE.md)
- ~~overview_agents.md~~
- ~~agent_spec_gec_ko.md~~
- ~~datasetguide.md~~
- ~~evaluation.md~~

---

## 빠른 네비게이션

### 처음 시작하는 경우
1. [01_GETTING_STARTED.md](./01_GETTING_STARTED.md) 읽기
2. 환경 설정 및 Baseline 실행
3. [02_EXPERIMENT_INSIGHTS.md](./02_EXPERIMENT_INSIGHTS.md) 읽기

### 기술 구현을 이해하려는 경우
1. [03_TECHNICAL_DETAILS.md](./03_TECHNICAL_DETAILS.md) 읽기
2. `code/src/` 디렉토리 탐색
3. 단위 테스트 확인 (`code/tests/`)

### 대회 정보를 확인하려는 경우
1. [04_COMPETITION_GUIDE.md](./04_COMPETITION_GUIDE.md) 읽기
2. 데이터셋 분석 (`data/train.csv`)
3. 제출 형식 확인

---

## 외부 링크

- **프로젝트 README**: [../README.md](../README.md)
- **코드 구조**: [../code/README.md](../code/README.md)
- **실험 결과**: [../outputs/README.md](../outputs/README.md)

---

**마지막 업데이트**: 2025-10-24
**구조 개편**: 30+ 문서 → 4개 핵심 문서로 통합
