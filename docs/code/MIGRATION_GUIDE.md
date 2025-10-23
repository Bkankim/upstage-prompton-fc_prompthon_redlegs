# 마이그레이션 가이드

기존 코드에서 새로운 모듈화된 구조로 전환하는 방법을 설명합니다.

## 주요 변경 사항 요약

### 1. 프롬프트 관리 시스템

**변경 전 (prompts.py)**
```python
# 단일 파일에 모든 프롬프트 하드코딩
BASELINE_PROMPT = {...}
FEWSHOT_PROMPT = {...}
ERROR_TYPES_PROMPT = {...}
```

**변경 후 (src/prompts/)**
```python
# 프롬프트 레지스트리 패턴 사용
from src.prompts.registry import get_registry, register_default_prompts

register_default_prompts()
registry = get_registry()
prompt = registry.get("baseline")
```

### 2. 문장 생성 로직

**변경 전 (baseline_generate.py, fewshot_v2_generate.py 등)**
```python
# 각 프롬프트마다 별도 스크립트
# 중복된 코드 존재
for text in texts:
    response = client.chat.completions.create(...)
```

**변경 후 (src/generator.py)**
```python
# 통합된 생성기 사용
from src.generator import SentenceGenerator

generator = SentenceGenerator(prompt_name="baseline")
result_df = generator.generate_batch(sentences)
```

### 3. 평가 로직

**변경 전 (evaluate.py, metrics.py)**
```python
# 직접 함수 호출
from metrics import calculate_recall
```

**변경 후 (src/evaluator.py, src/metrics/)**
```python
# Evaluator 클래스 사용
from src.evaluator import Evaluator

evaluator = Evaluator()
results = evaluator.evaluate(true_df, pred_df)
```

## 단계별 마이그레이션

### 단계 1: 기존 코드 백업

```bash
# 기존 코드 백업
cp baseline_generate.py baseline_generate.py.backup
cp evaluate.py evaluate.py.backup
cp prompts.py prompts.py.backup
```

### 단계 2: 새 모듈 사용하도록 스크립트 수정

#### 문장 생성 스크립트 업데이트

**기존 코드 (baseline_generate.py)**
```python
import os
from openai import OpenAI
from dotenv import load_dotenv
import pandas as pd
from tqdm import tqdm

load_dotenv()
api_key = os.getenv("UPSTAGE_API_KEY")
client = OpenAI(api_key=api_key, base_url="https://api.upstage.ai/v1")

# 프롬프트 하드코딩
PROMPT = {...}

# 수동 반복 처리
for text in tqdm(err_sentences):
    response = client.chat.completions.create(...)
    # ...
```

**새 코드**
```python
from src.generator import SentenceGenerator

# 간단한 초기화
generator = SentenceGenerator(
    prompt_name="baseline",  # 프롬프트 이름만 지정
    model="solar-pro2"
)

# CSV 파일 처리
generator.generate_from_csv(
    input_path="data/test.csv",
    output_path="outputs/baseline_test.csv"
)
```

#### 평가 스크립트 업데이트

**기존 코드 (evaluate.py)**
```python
from metrics import calculate_recall

# 수동 계산
tp = ...
fp = ...
fm = ...
recall = calculate_recall(tp, fp, fm)
```

**새 코드**
```python
from src.evaluator import Evaluator
import pandas as pd

# 간단한 초기화
evaluator = Evaluator()

# 데이터프레임으로 평가
true_df = pd.read_csv("data/train.csv")
pred_df = pd.read_csv("outputs/baseline_train.csv")

# 한 번에 평가
results = evaluator.evaluate(true_df, pred_df)

print(f"Recall: {results['recall']:.2f}%")
print(f"Precision: {results['precision']:.2f}%")
```

### 단계 3: 새 프롬프트 추가 시 레지스트리 사용

**기존 방식**
```python
# 새 프롬프트마다 새 스크립트 파일 생성
# myprompt_generate.py 생성
# 중복 코드 발생
```

**새 방식**
```python
# 1. src/prompts/myprompt.py 생성
from .base import BasePrompt

class MyPrompt(BasePrompt):
    @property
    def name(self) -> str:
        return "myprompt"

    def system_message(self) -> str:
        return "..."

    def format_user_message(self, text: str) -> str:
        return f"교정: {text}"

# 2. registry.py에 등록
def register_default_prompts():
    # ...
    registry.register(MyPrompt())

# 3. 기존 스크립트로 바로 사용
generator = SentenceGenerator(prompt_name="myprompt")
```

## 호환성 노트

### 하위 호환성

기존 스크립트는 계속 동작하지만, 새 모듈을 사용하는 것을 권장합니다.

- `baseline_generate.py` → `scripts/generate.py --prompt baseline` 사용 권장
- `fewshot_v2_generate.py` → `scripts/generate.py --prompt fewshot_v2` 사용 권장
- `evaluate.py` → `scripts/evaluate.py` 사용 권장

### 데이터 포맷

데이터 포맷은 변경되지 않았습니다. 기존 CSV 파일을 그대로 사용할 수 있습니다.

**필수 컬럼**
- 입력: `err_sentence` (교정할 문장)
- 출력: `cor_sentence` (교정된 문장)
- 평가: `err_sentence`, `cor_sentence` (정답 및 예측)

## 마이그레이션 체크리스트

- [ ] 기존 코드 백업 완료
- [ ] 새 디렉토리 구조 확인 (`src/`, `scripts/`, `tests/`)
- [ ] 프롬프트 레지스트리 이해
- [ ] SentenceGenerator 사용법 숙지
- [ ] Evaluator 사용법 숙지
- [ ] 기존 스크립트를 새 스크립트로 교체
- [ ] 테스트 실행 (`uv run pytest tests/`)
- [ ] 검증 스크립트 실행 (`uv run python scripts/verify_setup.py`)

## 예제: 전체 워크플로우 마이그레이션

### 기존 워크플로우

```bash
# 1. 프롬프트별로 개별 스크립트 실행
python baseline_generate.py
python fewshot_v2_generate.py
python errortypes_v3_generate.py

# 2. 각각 평가
python evaluate.py --truth data/train.csv --pred outputs/baseline.csv
python evaluate.py --truth data/train.csv --pred outputs/fewshot_v2.csv
python evaluate.py --truth data/train.csv --pred outputs/errortypes_v3.csv
```

### 새 워크플로우

```bash
# 1. 통합 스크립트로 실험 실행 (생성 + 평가)
uv run python scripts/run_experiment.py --prompt baseline --input data/train.csv
uv run python scripts/run_experiment.py --prompt fewshot_v2 --input data/train.csv
uv run python scripts/run_experiment.py --prompt errortypes_v3 --input data/train.csv

# 또는 개별 실행
uv run python scripts/generate.py --prompt baseline --input data/test.csv --output outputs/baseline_test.csv
uv run python scripts/evaluate.py --truth data/train.csv --prediction outputs/baseline_test.csv
```

## Python 코드에서 마이그레이션

### 프롬프트 사용

**기존**
```python
from prompts import BASELINE_PROMPT

# 프롬프트 직접 사용
prompt = BASELINE_PROMPT["prompt"]
system_msg = prompt["system"]
user_msg = prompt["user_turns"][0]["user"]
```

**새 방식**
```python
from src.prompts.registry import get_registry, register_default_prompts

register_default_prompts()
registry = get_registry()
prompt = registry.get("baseline")

# 자동 메시지 생성
messages = prompt.to_messages("교정할 문장")
# [
#   {"role": "user", "content": "..."},
# ]
```

### 메트릭 계산

**기존**
```python
from metrics import calculate_recall

tp = 10
fp = 2
fm = 3
recall = calculate_recall(tp, fp, fm)
```

**새 방식**
```python
from src.evaluator import Evaluator
import pandas as pd

true_df = pd.DataFrame({...})
pred_df = pd.DataFrame({...})

evaluator = Evaluator()
results = evaluator.evaluate(true_df, pred_df)

recall = results['recall']
precision = results['precision']
analysis_df = results['analysis_df']  # 상세 분석 데이터
```

## 트러블슈팅

### 문제 1: ImportError 발생

**증상**
```
ImportError: cannot import name 'BasePrompt' from 'src.prompts.base'
```

**해결**
```bash
# 현재 디렉토리 확인
pwd  # /Competition/.../code 에 있어야 함

# Python 경로 확인
uv run python -c "import sys; print(sys.path)"

# src/__init__.py 파일 존재 확인
ls src/__init__.py
```

### 문제 2: 프롬프트를 찾을 수 없음

**증상**
```
ValueError: Prompt 'baseline' not found in registry
```

**해결**
```python
# 프롬프트 등록 확인
from src.prompts.registry import get_registry, register_default_prompts

register_default_prompts()  # 반드시 호출
registry = get_registry()
print(registry.list_prompts())  # 등록된 프롬프트 목록 확인
```

### 문제 3: API 키 오류

**증상**
```
ValueError: UPSTAGE_API_KEY not found
```

**해결**
```bash
# .env 파일 확인
cat .env

# API 키가 없으면 추가
echo "UPSTAGE_API_KEY=your_key" > .env

# 또는 코드에서 직접 전달
generator = SentenceGenerator(
    prompt_name="baseline",
    api_key="your_api_key_here"
)
```

### 문제 4: 테스트 실패

**증상**
```
pytest tests/ 실행 시 실패
```

**해결**
```bash
# pytest 설치 확인
uv run pytest --version

# 개별 테스트 파일 실행
uv run pytest tests/test_prompts.py -v

# 특정 테스트만 실행
uv run pytest tests/test_prompts.py::TestPromptRegistry::test_registry_init -v
```

## 추가 리소스

- **README.md**: 프로젝트 전체 가이드
- **scripts/verify_setup.py**: 설정 검증 스크립트
- **tests/**: 예제 코드 및 사용법 참고

## 문의

마이그레이션 중 문제가 발생하면:
1. `scripts/verify_setup.py` 실행하여 설정 확인
2. 테스트 코드 참고 (`tests/`)
3. README.md의 사용 예시 확인
