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

### Final Result (Phase 1-6 완료)

```yaml
최종 확정:
  - Public LB: 34.0426%
  - Private LB: 13.4454%
  - 프롬프트: Baseline (맞춤법 예시 1개)
  - 파일: outputs/submissions/test/submission_baseline_test_clean.csv
  - 상태: 최종 확정 ✅

사용 제출: 4회 / 20회 (16회 남음)

주요 발견:
  - 1개 예시가 최적점 (0개: 보수적, 4개: 과적합)
  - Train 성능 향상 = Test 성능 하락
  - Public/Private 격차 20%p (근본적 한계)
  - 규칙 기반 후처리 효과 없음
```

### Experiment Summary

**전체 실험 이력**: [EXPERIMENT_LOG_SUMMARY.md](outputs/logs/EXPERIMENT_LOG_SUMMARY.md)

| Phase | 프롬프트 | 예시 | Public | Private | Train | 결과 |
|-------|---------|------|--------|---------|-------|------|
| 1 | **Baseline** | **1개** | **34.04%** | **13.45%** | 32.24% | ✅ **최종** |
| 2 | Zero-shot | 0개 | 31.91% | 12.61% | 32.24% | ❌ 보수적 |
| 2 | Plus3 | 4개 | 27.66% | 9.77% | 34.69% | ❌ 과적합 |
| 3 | 조사 | 1개 | 31.91% | 11.54% | 33.47% | ❌ 특화 실패 |
| 3 | 띄어쓰기 | 1개 | - | - | 32.65% | ❌ 폐기 |
| 6 | 규칙 후처리 | - | - | - | 32.24% | ❌ 효과 없음 |

### 핵심 교훈

#### 1. Few-shot의 양날의 검
```
0개 (Zero-shot): 31.91% - 보수적 (FN 증가)
1개 (Baseline):  34.04% - 최적 균형 ✅
4개 (Plus3):     27.66% - 과적합 (일반화 실패)
```

#### 2. 예시 설계의 중요성
- 다양성 > 특화: 맞춤법 예시 (3가지 오류) > 조사/띄어쓰기 (1가지 오류)
- 단일 예시의 복잡도가 중요

#### 3. Train 성능은 무의미
- Train 향상 → Test 하락 (모든 실험)
- **Train은 Test의 지표가 아님**

#### 4. Baseline의 강력함
- 명확한 규칙은 이미 100% 교정
- "금새→금세", "치 않→지 않" 등 완벽 처리
- **규칙 기반 후처리로 개선 불가능**

#### 5. 근본적 한계
- Public/Private 격차 20%p
- 데이터 분포 차이 (구조적 문제)
- 프롬프트 개선으로 해결 불가

### 상세 분석 문서

- **실험 종합**: [FINAL_EXPERIMENT_SUMMARY.md](outputs/analysis/FINAL_EXPERIMENT_SUMMARY.md)
- **Plus3 실패 분석**: [FAILURE_ANALYSIS_BASELINE_PLUS_3EXAMPLES.md](outputs/analysis/FAILURE_ANALYSIS_BASELINE_PLUS_3EXAMPLES.md)
- **규칙 후처리 실험**: [FINAL_MINIMAL_RULES_EXPERIMENT.md](outputs/analysis/FINAL_MINIMAL_RULES_EXPERIMENT.md)
- **전문가 조언 전략**: [EXPERT_ADVICE_STRATEGY.md](docs/advanced/EXPERT_ADVICE_STRATEGY.md)

## etc

### Reference

- 대회 페이지: https://stages.ai/en/competitions/403
- Upstage Console: https://console.upstage.ai/
- LCS 알고리즘: https://ko.wikipedia.org/wiki/최장_공통_부분_수열
- Precision/Recall: https://en.wikipedia.org/wiki/Precision_and_recall