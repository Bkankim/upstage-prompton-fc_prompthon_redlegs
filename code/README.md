# 한국어 문법 교정 시스템

Upstage Global Eval Challenge (GEC) - Promptathon 대회를 위한 한국어 문법 교정 시스템입니다. 프롬프트 엔지니어링을 통해 Solar Pro 2 모델로 문법 교정을 수행하며, Recall 최대화를 목표로 합니다.

## 프로젝트 구조

```
code/
├── src/                          # 핵심 소스 코드
│   ├── prompts/                  # 프롬프트 관리
│   │   ├── base.py              # 프롬프트 기본 추상 클래스
│   │   ├── baseline.py          # 베이스라인 프롬프트
│   │   ├── fewshot_v2.py        # Few-shot 프롬프트
│   │   ├── errortypes_v3.py     # 오류 유형별 프롬프트
│   │   ├── registry.py          # 프롬프트 레지스트리
│   │   └── __init__.py
│   ├── metrics/                  # 평가 메트릭
│   │   ├── lcs.py               # LCS 기반 차이점 검출
│   │   ├── evaluator.py         # Recall/Precision 계산
│   │   └── __init__.py
│   ├── generator.py              # 문장 생성기 (통합)
│   └── evaluator.py              # 평가 실행기
├── scripts/                      # 실행 스크립트
│   ├── generate.py              # 문장 생성 스크립트
│   ├── evaluate.py              # 평가 실행 스크립트
│   └── run_experiment.py        # 실험 통합 실행
├── tests/                        # 테스트 코드
│   ├── test_prompts.py          # 프롬프트 테스트
│   ├── test_metrics.py          # 메트릭 테스트
│   ├── test_generator.py        # 생성기 테스트
│   └── test_evaluator.py        # 평가기 테스트
├── data/                         # 데이터 파일
│   ├── train.csv                # 학습 데이터 (254개)
│   ├── test.csv                 # 테스트 데이터 (109개)
│   └── sample_submissioncsv.csv # 제출 형식 샘플
├── outputs/                      # 실험 결과 (Git 제외)
├── configs/                      # 설정 파일
├── docs/                         # 문서
│   └── MIGRATION_GUIDE.md       # 마이그레이션 가이드
├── pyproject.toml                # Python 의존성 정의
├── .python-version               # Python 3.12
├── .env                          # API 키 설정 (Git 제외)
└── README.md                     # 이 파일
```

## 빠른 시작

### 1. 환경 설정

이 프로젝트는 **uv**를 사용하여 Python 환경을 관리합니다.

```bash
# uv 설치 (필요한 경우)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 프로젝트 디렉토리로 이동
cd /Competition/upstage-prompton-fc_prompthon_redlegs/code

# 의존성 설치
uv sync
```

### 2. API 키 설정

`.env` 파일을 생성하고 Upstage API 키를 설정합니다.

```bash
echo "UPSTAGE_API_KEY=your_api_key_here" > .env
```

### 3. 문장 교정 생성

프롬프트를 선택하여 문장 교정을 수행합니다.

```bash
# 베이스라인 프롬프트 사용
uv run python scripts/generate.py --prompt baseline --input data/test.csv --output outputs/baseline_test.csv

# Few-shot 프롬프트 사용
uv run python scripts/generate.py --prompt fewshot_v2 --input data/test.csv --output outputs/fewshot_v2_test.csv

# 오류 유형별 프롬프트 사용
uv run python scripts/generate.py --prompt errortypes_v3 --input data/test.csv --output outputs/errortypes_v3_test.csv
```

### 4. 평가 실행

생성된 결과를 평가합니다.

```bash
uv run python scripts/evaluate.py --truth data/train.csv --prediction outputs/baseline_test.csv
```

### 5. 통합 실험 실행

생성과 평가를 한 번에 수행합니다.

```bash
uv run python scripts/run_experiment.py --prompt baseline --input data/train.csv --output outputs/baseline_train.csv
```

## 사용 예시

### Python 코드에서 사용하기

#### 1. 프롬프트 레지스트리 사용

```python
from src.prompts.registry import get_registry, register_default_prompts

# 기본 프롬프트 등록
register_default_prompts()

# 레지스트리 조회
registry = get_registry()

# 사용 가능한 프롬프트 목록
print(registry.list_prompts())
# ['baseline', 'fewshot_v2', 'errortypes_v3']

# 특정 프롬프트 조회
prompt = registry.get("baseline")
print(prompt.name)  # 'baseline'

# 프롬프트를 메시지로 변환
messages = prompt.to_messages("오늘 날씨가 않좋다")
```

#### 2. SentenceGenerator 사용

```python
from src.generator import SentenceGenerator

# 생성기 초기화 (프롬프트 이름 지정)
generator = SentenceGenerator(
    prompt_name="baseline",
    model="solar-pro2"
)

# 단일 문장 교정
corrected = generator.generate_single("오늘 날씨가 않좋다")
print(corrected)  # "오늘 날씨가 안 좋다"

# 배치 교정
sentences = ["문장1", "문장2", "문장3"]
result_df = generator.generate_batch(sentences)

# CSV 파일 처리
generator.generate_from_csv(
    input_path="data/test.csv",
    output_path="outputs/result.csv"
)
```

#### 3. Evaluator 사용

```python
import pandas as pd
from src.evaluator import Evaluator

# 평가기 초기화
evaluator = Evaluator()

# 정답 데이터 로드
true_df = pd.read_csv("data/train.csv")

# 예측 데이터 로드
pred_df = pd.read_csv("outputs/baseline_train.csv")

# 평가 수행
results = evaluator.evaluate(true_df, pred_df)

# 결과 출력
print(f"Recall: {results['recall']:.2f}%")
print(f"Precision: {results['precision']:.2f}%")
print(f"True Positives: {results['true_positives']}")
print(f"False Positives: {results['false_positives']}")
print(f"False Missings: {results['false_missings']}")

# 상세 분석 데이터
analysis_df = results['analysis_df']
```

## 새 프롬프트 추가 방법

프롬프트 시스템은 확장 가능한 구조로 설계되어 있습니다. 새로운 프롬프트를 쉽게 추가할 수 있습니다.

### 1. 프롬프트 클래스 작성

`src/prompts/` 디렉토리에 새 파일을 생성합니다 (예: `mypromppt_v1.py`).

```python
"""
커스텀 프롬프트 클래스
"""

from .base import BasePrompt


class MyPromptV1(BasePrompt):
    """
    커스텀 프롬프트 설명
    """

    @property
    def name(self) -> str:
        """프롬프트 이름 반환"""
        return "myprompt_v1"

    def system_message(self) -> str:
        """
        시스템 메시지 반환
        시스템 메시지가 필요 없으면 빈 문자열 반환
        """
        return "당신은 한국어 문법 교정 전문가입니다."

    def format_user_message(self, text: str) -> str:
        """
        사용자 메시지 포맷팅

        Args:
            text: 교정할 원문 텍스트

        Returns:
            str: 포맷팅된 프롬프트
        """
        template = """다음 문장을 교정하세요:

원문: {text}

교정:"""
        return template.format(text=text)
```

### 2. 레지스트리에 등록

`src/prompts/registry.py` 파일의 `register_default_prompts()` 함수를 수정합니다.

```python
def register_default_prompts() -> None:
    """
    기본 프롬프트들을 레지스트리에 자동 등록
    """
    from .baseline import BaselinePrompt
    from .fewshot_v2 import FewshotV2Prompt
    from .errortypes_v3 import ErrorTypesV3Prompt
    from .myprompt_v1 import MyPromptV1  # 추가

    registry = get_registry()
    registry.register(BaselinePrompt())
    registry.register(FewshotV2Prompt())
    registry.register(ErrorTypesV3Prompt())
    registry.register(MyPromptV1())  # 추가
```

### 3. 사용하기

이제 새 프롬프트를 다른 프롬프트와 동일하게 사용할 수 있습니다.

```bash
# CLI에서 사용
uv run python scripts/generate.py --prompt myprompt_v1 --input data/test.csv --output outputs/myprompt_v1_test.csv

# Python 코드에서 사용
from src.generator import SentenceGenerator

generator = SentenceGenerator(prompt_name="myprompt_v1")
result = generator.generate_single("오늘 날씨가 않좋다")
```

## 테스트 실행

프로젝트의 모든 테스트를 실행합니다.

```bash
# 전체 테스트 실행
uv run pytest tests/ -v

# 특정 테스트 파일만 실행
uv run pytest tests/test_prompts.py -v

# 커버리지 포함 테스트
uv run pytest tests/ --cov=src --cov-report=html
```

## 평가 메트릭 설명

### Recall (재현율)

- 정의: `TP / (TP + FP + FM) × 100`
- 의미: 실제 오류 중 얼마나 교정했는가
- 대회 목표: Recall 최대화

### Precision (정밀도)

- 정의: `TP / (TP + FP + FR) × 100`
- 의미: 교정한 것 중 얼마나 정확한가

### 용어 설명

- **TP (True Positive)**: 올바르게 교정한 부분
- **FP (False Positive)**: 잘못 교정한 부분
- **FM (False Missing)**: 놓친 오류 (교정하지 않음)
- **FR (False Redundant)**: 불필요한 교정 (정상 부분을 수정)

## 프롬프트 종류

### 1. baseline

- 단순하고 직접적인 교정 지시
- Few-shot 예시 1개 포함
- 가장 간단한 구조

### 2. fewshot_v2

- Few-shot Learning 기반
- 다양한 오류 유형별 예시 제공
- System message 포함

### 3. errortypes_v3

- 오류 유형별 상세 분석
- 단계별 추론 과정 포함
- 가장 복잡한 구조

## 대회 제약사항

- 세션당 최대 토큰: 2000
- 케이스당 최대 API 호출: 3회
- 일일 제출 제한: 20회 (KST 자정 리셋)
- 외부 데이터 사용 금지
- RAG는 제공 데이터셋 내부만 허용

## 기술 스택

- Python 3.12
- uv (패키지 관리)
- Upstage Solar Pro 2 (교정 모델)
- OpenAI SDK (API 통신)
- pandas (데이터 처리)
- pytest (테스트)

## 라이선스

이 프로젝트는 대회 참여를 위한 코드이며, 외부 공유나 상업적 이용은 허용되지 않습니다.

## 문의

- 대회 관련: Upstage Global Eval Challenge 운영진
- 기술 문제: 코드 이슈 트래커 활용
