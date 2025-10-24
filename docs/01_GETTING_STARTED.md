# 시작하기

> 5분 안에 프로젝트 실행 및 재현

## 사전 요구사항

- Python 3.12+
- Git
- Upstage API 키 ([발급 링크](https://console.upstage.ai/))

---

## 환경 설정 (3단계)

### 1. uv 설치

```bash
# uv 패키지 관리자 설치
curl -LsSf https://astral.sh/uv/install.sh | sh

# 설치 확인
uv --version
```

**uv를 사용하는 이유:**
- 의존성 관리 일관성 (pyproject.toml 기반)
- Python 3.12 환경 자동 보장
- 격리된 가상 환경 (.venv)
- 재현성 보장

### 2. 프로젝트 클론 및 의존성 설치

```bash
# 프로젝트 클론
git clone <repository-url>
cd upstage-prompton-fc_prompthon_redlegs/code

# 의존성 자동 설치
uv sync
```

### 3. API 키 설정

```bash
# .env 파일 생성
echo "UPSTAGE_API_KEY=your_api_key_here" > .env
```

---

## 빠른 실행

### Baseline 실험 재현

```bash
# code 디렉토리에서
cd code

# Train 데이터 교정 + 평가
uv run python scripts/run_experiment.py --prompt baseline
```

**결과물:**
- `outputs/submissions/train/submission_baseline.csv`: Train 교정 결과
- `outputs/submissions/test/submission_baseline_test.csv`: Test 제출 파일 (LB용)
- `outputs/logs/baseline_results.json`: Recall/Precision 메트릭
- `outputs/analysis/analysis_baseline.csv`: 상세 케이스별 분석

### 결과 확인

```bash
# Recall/Precision 확인
cat outputs/logs/baseline_results.json

# 예상 출력:
# {
#   "prompt": "baseline",
#   "train_performance": {
#     "recall": 32.24,
#     "precision": 14.79
#   }
# }
```

---

## 프로젝트 구조

```
code/
├── scripts/
│   ├── generate.py          # 교정 실행
│   ├── evaluate.py           # 평가 실행
│   └── run_experiment.py     # 통합 실험 스크립트
├── src/
│   ├── prompts/              # 프롬프트 템플릿
│   │   ├── baseline.py       # 최고 성능 (34.04%)
│   │   ├── zero_shot.py      # 실패 사례 1
│   │   ├── baseline_plus_3examples.py  # 실패 사례 2
│   │   └── baseline_josa.py  # 실패 사례 3
│   ├── metrics/              # 평가 지표 (Recall 계산)
│   ├── generator.py          # 교정 생성기
│   └── evaluator.py          # 평가 클래스
├── data/
│   ├── train.csv             # 254개 학습 데이터
│   └── test.csv              # 109개 테스트 데이터
├── outputs/
│   ├── submissions/          # 교정 결과 CSV
│   ├── logs/                 # 평가 메트릭 JSON
│   └── analysis/             # 상세 분석 CSV
├── tests/                    # 단위 테스트 (85개)
├── pyproject.toml            # 의존성 정의
└── .env                      # API 키 (git 제외)
```

---

## 핵심 명령어

### 실험 실행

**중요: 모든 실행은 반드시 `uv run` 사용!**

```bash
# ✅ 올바른 방법
uv run python scripts/generate.py --prompt baseline
uv run python scripts/evaluate.py

# ❌ 절대 금지 (의존성 오류 발생)
python scripts/generate.py
python3 scripts/evaluate.py
```

### 다른 프롬프트 실험

```bash
# Zero-shot (예시 0개) - 31.91% Public
uv run python scripts/run_experiment.py --prompt zero_shot

# Plus3 (예시 4개) - 27.66% Public (실패)
uv run python scripts/run_experiment.py --prompt baseline_plus_3examples

# 조사 특화 (예시 1개) - 31.91% Public (실패)
uv run python scripts/run_experiment.py --prompt baseline_josa
```

### 테스트 실행

```bash
# 전체 테스트 (85개)
uv run pytest tests/ -v

# 특정 모듈만
uv run pytest tests/test_prompts.py -v
```

---

## 코드 구조 이해

### 프롬프트 정의

```python
# src/prompts/baseline.py
class BaselinePrompt:
    """
    최고 성능 프롬프트 (34.04% Public)
    - 1개 Few-shot 예시
    - 다양한 오류 유형 포함 (맞춤법, 띄어쓰기, 문법)
    """
    def get_prompt(self, err_sentence: str) -> dict:
        return {
            "messages": [
                {
                    "role": "system",
                    "content": "당신은 한국어 문법 전문가입니다..."
                },
                {
                    "role": "user",
                    "content": f"<원문>\n{err_sentence}\n<교정>\n"
                }
            ]
        }
```

### 평가 메트릭

```python
# src/metrics/evaluator.py
from src.metrics.lcs import calculate_lcs_recall

# Recall = TP / (TP + FP + FN) × 100
# TP: 정답과 예측이 일치하는 어절
# FP: 예측에만 있는 어절 (잘못 추가)
# FN: 정답에만 있는 어절 (놓침)
```

### 실험 자동화

```python
# scripts/run_experiment.py
# 1단계: Train 데이터 교정
# 2단계: Train 데이터 평가 (Recall/Precision)
# 3단계: Test 데이터 교정 (LB 제출용)
# 4단계: 결과 저장 (outputs/)
```

---

## 데이터 형식

### train.csv / test.csv

```csv
id,err_sentence,cor_sentence,type
grm123456,"오류 문장","교정 문장","맞춤법-맞춤법"
...
```

**오류 유형:**
- 맞춤법-맞춤법, 맞춤법-사이시옷
- 문법-품사, 문법-조사
- 표준어비표준어
- 문장부호-문장부호
- 띄어쓰기
- 비문, 단순오탈자, 기타 등

### submission.csv (제출 형식)

```csv
id,err_sentence,cor_sentence
grm123456,"오류 문장","프롬프트로 교정한 문장"
...
```

---

## 문제 해결

### Import Error

```
ImportError: cannot import name 'xxx'
```

**해결**: uv 환경에서 실행하지 않았을 가능성
```bash
# 반드시 uv run 사용
uv run python scripts/generate.py
```

### API Key Error

```
Error: UPSTAGE_API_KEY not found
```

**해결**: .env 파일 확인
```bash
# .env 파일이 code/ 디렉토리에 있는지 확인
cat .env

# 없으면 생성
echo "UPSTAGE_API_KEY=your_key" > .env
```

### 의존성 오류

```
ModuleNotFoundError: No module named 'xxx'
```

**해결**: 의존성 재설치
```bash
uv sync --reinstall
```

---

## 다음 단계

1. **실험 인사이트 읽기**: [02_EXPERIMENT_INSIGHTS.md](./02_EXPERIMENT_INSIGHTS.md)
   - Phase 1-6 실험 과정
   - 실패 사례 및 교훈
   - 핵심 발견 5가지

2. **기술 상세 확인**: [03_TECHNICAL_DETAILS.md](./03_TECHNICAL_DETAILS.md)
   - 아키텍처 설계
   - 평가 지표 구현
   - 고급 프롬프트 기법

3. **대회 정보 확인**: [04_COMPETITION_GUIDE.md](./04_COMPETITION_GUIDE.md)
   - 대회 규칙 및 제약사항
   - 평가 방식
   - 데이터셋 구성

---

## 참고 자료

- Upstage Solar Pro 2: [공식 문서](https://console.upstage.ai/docs/capabilities/chat)
- uv 패키지 관리자: [공식 사이트](https://github.com/astral-sh/uv)
- 프로젝트 구조: [코드 README](../code/README.md)
- 실험 결과: [outputs README](../outputs/README.md)

---

**작성일**: 2025-10-24
**대상**: 신규 사용자 및 프로젝트 재현
