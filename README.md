# GEC Promptathon - 한국어 문법 교정 프롬프트 최적화
## Team Red Legs

프롬프트 엔지니어링을 통한 한국어 문법 교정 시스템 개발

## 0. Overview
### Environment
- Python 3.12
- uv (패키지 관리)
- Upstage Solar Pro 2 모델

### Requirements

**⚠️ 중요: 모든 Python 실행은 반드시 uv 환경에서!**
- 상세 가이드: [UV_ENVIRONMENT_GUIDE.md](docs/getting-started/UV_ENVIRONMENT_GUIDE.md)

```bash
# 1. uv 설치 (필수!)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. 의존성 설치
cd code && uv sync

# 3. API 키 설정
echo "UPSTAGE_API_KEY=your_key_here" > .env

# 4. 실행 예시 (반드시 uv run 사용!)
uv run python scripts/generate.py --prompt baseline  # ✅ 올바른 방법
# python scripts/generate.py                         # ❌ 절대 금지!
```

## 1. Competition Info

### Overview

- **대회명**: Upstage Global Eval Challenge (GEC) - Promptathon
- **목표**: 프롬프트 엔지니어링으로 한국어 문법 교정 시스템 개발
- **평가지표**: Recall (재현율) - TP/(TP+FP+FN) × 100
- **데이터**: Train 254개, Test 109개
- **제약사항**: 세션 토큰 2000개, API 호출 3회/케이스, 일일 제출 20회

### Timeline

- 2024년 10월 - 대회 시작
- 진행 중

## 2. Components

### Directory

```
├── code/                       # 베이스라인 및 실험 코드
│   ├── scripts/                # 실행 스크립트
│   │   ├── generate.py         # 교정 실행 (통합 스크립트)
│   │   ├── evaluate.py         # 평가 실행
│   │   └── run_experiment.py   # 실험 자동화
│   ├── src/                    # 소스 모듈
│   │   ├── prompts/            # 프롬프트 템플릿 (핵심)
│   │   ├── metrics/            # 평가 메트릭
│   │   ├── generator.py        # 통합 생성기
│   │   └── evaluator.py        # 평가 클래스
│   ├── tests/                  # 테스트 (85개)
│   └── data/                   # 데이터셋
├── docs/                       # 문서
│   ├── getting-started/        # 신규 사용자 가이드
│   │   ├── QUICK_START.md      # 5분 시작 가이드
│   │   ├── UV_ENVIRONMENT_GUIDE.md
│   │   └── BASELINE_CODE.md
│   ├── advanced/               # 고급 전략
│   │   ├── ADVANCED_STRATEGIES.md  # 최신 기법 (2024-2025)
│   │   └── EXPERIMENT_LESSONS.md   # 실험 교훈
│   ├── competition/            # 대회 공식 문서
│   │   ├── overview_agents.md
│   │   ├── agent_spec_gec_ko.md
│   │   ├── datasetguide.md
│   │   └── evaluation.md
│   └── code/                   # 코드 문서
│       ├── GENERATOR_ARCHITECTURE.md
│       └── MIGRATION_GUIDE.md
├── tasks/                      # PRD 및 태스크
│   ├── prd-gec-prompt-optimization-system.md
│   └── tasks-prd-gec-prompt-optimization-system.md
├── outputs/logs/               # 실험 로그
│   ├── EXPERIMENT_LOG_SUMMARY.md
│   └── experiments/            # 상세 분석
└── code/outputs/submissions/   # 제출 파일
```

## 3. Data Description

### Dataset Overview

- **Train**: 254개 문장 (오류 유형 포함)
- **Test**: 109개 문장 (Public 40%, Private 60%)
- **오류 유형**: 조사오류(16.1%), 사이시옷(13.4%), 표준어(9.4%), 어휘(8.7%) 등 20종

### EDA

- 오류 유형별 분포 분석 완료
- 평균 문장 길이: 136.8자
- 60%는 교정 후 길이 변화 없음
- 주요 패턴: 조사 오류, 맞춤법, 띄어쓰기

### Data Processing

- CSV 형식 (err_sentence, cor_sentence)
- 토큰화: 공백 기준 분할
- 평가: LCS 알고리즘 기반

## 4. Modeling

### Model Description

- **모델**: Upstage Solar Pro 2
- **접근법**: 프롬프트 엔지니어링 (파인튜닝 없음)
- **전략**:
  - 베이스라인 프롬프트
  - Few-shot Learning
  - Chain-of-Thought
  - Multi-turn 검증

### Modeling Process

1. **베이스라인 성능 측정**
2. **프롬프트 개선 전략 실험**
3. **최적 템플릿 선택**
4. **최종 제출 파일 생성**

## 5. Result

### Leader Board (2025-10-23 기준)

```yaml
최고 성능:
  - Public LB: 34.0426%
  - Private LB: 13.4454%
  - 프롬프트: Baseline (Response Cleaning)
  - 파일: outputs/submissions/test/submission_baseline_test_clean.csv

진행 중:
  - 개선 버전: 콜론 버그 수정 + 문법 규칙 복원
  - Train Recall: 33.88%
  - 상태: LB 제출 대기

주요 이슈:
  - Public/Private 격차: 약 20%p (비정상적)
  - 일반적 격차: 5-10%p
  - 추정 원인: 데이터 분포 차이
```

### Experiment Log

**전체 실험 이력**: [EXPERIMENT_LOG_SUMMARY.md](outputs/logs/EXPERIMENT_LOG_SUMMARY.md)

| # | 프롬프트 | Train Recall | Public LB | Private LB | 상태 |
|---|---------|--------------|-----------|------------|------|
| 1 | **Baseline** | 32.24% | **34.04%** | **13.45%** | ✅ 최고 |
| 2 | Few-shot v2 | 35.92% | 31.91% | 12.10% | ❌ 과적합 |
| 6 | Rule-Checklist (버그) | 33.88% | 31.91% | 12.80% | ❌ 콜론 버그 |
| 7 | **Rule-Checklist (개선)** | 33.88% | ? | ? | 🔄 제출 대기 |

### 전문가 조언 기반 개선 전략

**상세 문서**: [EXPERT_ADVICE_STRATEGY.md](docs/advanced/EXPERT_ADVICE_STRATEGY.md)

```
우선순위:

[오늘 즉시]
1. 규칙별 순효과 분석 (문법 규칙 유지/제거 결정)
2. 60% 길이 가드 구현 (83% 손실 재발 방지)
3. 개선 버전 LB 제출 (콜론 버그 수정 효과 검증)

[내일]
4. 5-fold 교차검증 (Public/Private 격차 원인 규명)
5. 유형별 성과 분석 (취약 유형 식별)
6. 프롬프트 형식 제약 A/B (메타데이터 억제)

[목표]
- Public: 35-36%, Private: 14-15%
- Public/Private 격차: 20%p → 15%p 이하
- 일관성 있는 성능 확보
```

### 최근 발견 및 수정

**콜론 버그 (해결 완료)**:
- 문제: "7:3" → "3" 변환으로 83% 텍스트 손실 (8개 케이스)
- 원인: 비율/시간 표기를 메타데이터 콜론으로 오인
- 해결: 3단계 검증 로직 구현 (숫자 패턴 체크 → 위치 체크 → 키워드 체크)
- 검증: test_improved_logic.py 통과

**전략 변경**:
```diff
- ❌ 기존: 고급 프롬프트 기법 (CD-CoT, ToT) 우선
+ ✅ 변경: 기본 안정화 + 일반화 문제 해결 우선

이유: Public/Private 격차(20%p)가 더 심각한 문제
```

## etc

### Reference

- 대회 페이지: https://stages.ai/en/competitions/403
- Upstage Console: https://console.upstage.ai/
- LCS 알고리즘: https://ko.wikipedia.org/wiki/최장_공통_부분_수열
- Precision/Recall: https://en.wikipedia.org/wiki/Precision_and_recall