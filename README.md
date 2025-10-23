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

### Leader Board

- **목표**: Recall 75% 이상
- **현재 상태**: 베이스라인 측정 대기
- **진행 중**

### Experiment Log

- 베이스라인 성능: 측정 예정
- 실험 결과: `logs/` 디렉토리에 저장 예정

## etc

### Reference

- 대회 페이지: https://stages.ai/en/competitions/403
- Upstage Console: https://console.upstage.ai/
- LCS 알고리즘: https://ko.wikipedia.org/wiki/최장_공통_부분_수열
- Precision/Recall: https://en.wikipedia.org/wiki/Precision_and_recall