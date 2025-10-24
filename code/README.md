# 코드 구조

## 디렉토리 구조

```
code/
├── scripts/               # 실행 스크립트
│   ├── generate.py        # 교정 실행
│   ├── evaluate.py        # 평가 실행
│   ├── run_experiment.py  # 통합 실험 (교정 + 평가 + Test 생성)
│   └── verify_setup.py    # 환경 검증
├── src/                   # 소스 모듈
│   ├── prompts/           # 프롬프트 템플릿
│   │   ├── base.py        # 기본 클래스
│   │   ├── baseline.py    # 최고 성능 (34.04%)
│   │   ├── zero_shot.py   # 실패 사례 1 (31.91%)
│   │   ├── baseline_plus_3examples.py  # 실패 사례 2 (27.66%)
│   │   └── baseline_josa.py            # 실패 사례 3 (31.91%)
│   ├── metrics/           # 평가 지표
│   │   ├── evaluator.py   # Recall/Precision 계산
│   │   └── lcs.py         # LCS 알고리즘
│   ├── postprocessors/    # 후처리
│   │   ├── base.py
│   │   ├── enhanced_postprocessor.py
│   │   ├── minimal_rule.py    # Phase 6 규칙 기반
│   │   └── rule_checklist.py
│   ├── generator.py       # 교정 생성기
│   └── evaluator.py       # 평가 클래스 (레거시)
├── tests/                 # 단위 테스트 (85개)
│   ├── test_prompts.py
│   ├── test_evaluator.py
│   ├── test_generator.py
│   ├── test_metrics.py
│   └── test_postprocessors.py
├── data/                  # 데이터셋
│   ├── train.csv          # 254개
│   └── test.csv           # 109개
├── outputs/               # 실험 결과
│   ├── submissions/       # 교정 결과 CSV
│   ├── logs/              # 평가 메트릭 JSON
│   └── analysis/          # 상세 분석 CSV
├── pyproject.toml         # 의존성 정의
├── .python-version        # Python 3.12
└── .env                   # API 키 (git 제외)
```

---

## 핵심 모듈

### 1. Prompts (`src/prompts/`)

모든 프롬프트의 기본 클래스:
```python
# src/prompts/base.py
class BasePrompt:
    def get_prompt(self, err_sentence: str) -> dict:
        """Upstage API 형식의 프롬프트 반환"""
        raise NotImplementedError
```

**주요 프롬프트:**

| 파일 | 클래스 | 예시 | 성능 | 상태 |
|------|--------|------|------|------|
| `baseline.py` | BaselinePrompt | 1개 | 34.04% | [완료] 최고 |
| `zero_shot.py` | ZeroShotPrompt | 0개 | 31.91% | [실패] 보수적 |
| `baseline_plus_3examples.py` | BaselinePlus3ExamplesPrompt | 4개 | 27.66% | [실패] 과적합 |
| `baseline_josa.py` | BaselineJosaPrompt | 1개 (조사) | 31.91% | [실패] 특화 실패 |

### 2. Generator (`src/generator.py`)

```python
class Generator:
    """
    프롬프트를 사용해 교정 문장을 생성
    """
    def generate(self, prompt_class, data: pd.DataFrame) -> List[str]:
        # 1. 각 케이스별로 프롬프트 생성
        # 2. Upstage API 호출 (최대 3회)
        # 3. 응답 정제 (메타데이터 제거)
        # 4. 결과 반환
```

### 3. Evaluator (`src/metrics/evaluator.py`)

```python
class Evaluator:
    """
    LCS 기반 Recall/Precision 계산
    """
    def evaluate(self, true_df, pred_df) -> dict:
        # TP/FP/FN 계산
        # Recall = TP / (TP + FP + FN) × 100
        # Precision = TP / (TP + FP) × 100
```

### 4. Postprocessors (`src/postprocessors/`)

후처리기 (메타데이터 제거, 규칙 적용 등):

- `enhanced_postprocessor.py`: 메타데이터 제거 시도
- `rule_checklist.py`: 국립국어원 규칙 기반
- `minimal_rule.py`: Phase 6 실험 (규칙 적용 0개)

---

## 실험 스크립트 (6개 보존)

### 핵심 실험

| 파일 | 목적 | 사용 Phase |
|------|------|-----------|
| `validate_baseline_minimal_rules.py` | Phase 6 규칙 후처리 검증 | Phase 6 |
| `analyze_fewshot_failure.py` | Plus3 실패 분석 | Phase 2 |
| `extract_clear_rules.py` | Train 데이터에서 규칙 추출 | Phase 6 |
| `compare_versions.py` | 프롬프트 간 비교 | Phase 3-5 |
| `select_phase3_samples.py` | Phase 3 샘플 선택 | Phase 3 |
| `generate_test_submission.py` | Test 제출 파일 생성 | 전체 |

---

## 사용 방법

### 환경 설정

```bash
# code 디렉토리로 이동
cd code

# 의존성 설치
uv sync

# API 키 설정
echo "UPSTAGE_API_KEY=your_key" > .env
```

### 실험 실행

**통합 스크립트** (권장):
```bash
# Train 교정 + 평가 + Test 생성을 한 번에
uv run python scripts/run_experiment.py --prompt baseline
```

**개별 스크립트**:
```bash
# 1. Train 데이터 교정
uv run python scripts/generate.py --prompt baseline

# 2. 평가 실행
uv run python scripts/evaluate.py

# 3. Test 데이터 교정 (LB 제출용)
uv run python generate_test_submission.py
```

### 테스트 실행

```bash
# 전체 테스트 (85개)
uv run pytest tests/ -v

# 커버리지 확인
uv run pytest tests/ --cov=src --cov-report=html
```

---

## 결과물 확인

### Train 결과

```bash
# 교정 파일
cat outputs/submissions/train/submission_baseline.csv

# 평가 메트릭
cat outputs/logs/baseline_results.json

# 상세 분석
cat outputs/analysis/analysis_baseline.csv
```

### Test 결과 (LB 제출용)

```bash
# LB 제출 파일
cat outputs/submissions/test/submission_baseline_test.csv

# 파일 형식 확인
head -3 outputs/submissions/test/submission_baseline_test.csv
# id,err_sentence,cor_sentence
# grm123456,"오류 문장","교정 문장"
```

---

## 새로운 프롬프트 추가

### 1. 프롬프트 클래스 작성

```python
# src/prompts/my_prompt.py
from src.prompts.base import BasePrompt

class MyPrompt(BasePrompt):
    def get_prompt(self, err_sentence: str) -> dict:
        return {
            "messages": [
                {
                    "role": "system",
                    "content": "당신은 한국어 전문가입니다..."
                },
                {
                    "role": "user",
                    "content": f"<원문>\n{err_sentence}\n<교정>\n"
                }
            ]
        }
```

### 2. 실험 실행

```bash
uv run python scripts/run_experiment.py --prompt my_prompt
```

### 3. 결과 확인

```bash
cat outputs/logs/my_prompt_results.json
```

---

## 주의사항

### 필수: uv 환경 사용

```bash
# [완료] 올바른 방법
uv run python scripts/generate.py

# [실패] 절대 금지 (의존성 오류)
python scripts/generate.py
python3 scripts/generate.py
```

### API 제약사항

- 세션당 2000 토큰 제한
- 케이스당 최대 3회 API 호출
- 일일 제출 20회 제한

### 데이터 경로

```python
# 절대 경로 권장
DATA_PATH = "code/data/train.csv"

# 상대 경로 (code/ 디렉토리 기준)
DATA_PATH = "data/train.csv"
```

---

## 참고 자료

### 프로젝트 문서

- **실험 인사이트**: [docs/02_EXPERIMENT_INSIGHTS.md](../docs/02_EXPERIMENT_INSIGHTS.md)
- **기술 상세**: [docs/03_TECHNICAL_DETAILS.md](../docs/03_TECHNICAL_DETAILS.md)
- **시작 가이드**: [docs/01_GETTING_STARTED.md](../docs/01_GETTING_STARTED.md)

### 외부 링크

- Upstage API: https://console.upstage.ai/docs
- uv 패키지 관리자: https://github.com/astral-sh/uv

---

**마지막 업데이트**: 2025-10-24
**구조 개편**: 80+ 스크립트 → 6개 핵심 + 5개 프롬프트로 정리
