# BASELINE_CODE.md

프롬프트 해커톤을 위한 베이스라인 코드 가이드입니다.

---

# 📁 파일 구조
```yaml
baseline_code/:
  scripts:
    baseline_generate.py:
      purpose: "교정 문장 생성"
      input: "data/train_dataset.csv"
      output: "submission.csv"
      
    evaluate.py:
      purpose: "평가 실행"
      metrics: ["Recall", "Precision"]
      output: "analysis.csv"
      
    metrics.py:
      purpose: "평가 메트릭 계산"
      functions: ["calculate_recall", "calculate_precision"]
      
    prompts.py:
      purpose: "프롬프트 템플릿 관리"
      note: "이 파일을 수정하여 성능 개선"
      priority: "highest"
  
  config:
    pyproject.toml:
      purpose: "Python 의존성 관리"
      
    .python-version:
      purpose: "Python 버전 명시"
      
    .env.example:
      purpose: "환경 변수 예시"
      note: ".env 파일을 생성하여 실제 API 키 입력"
  
  data:
    train_dataset.csv:
      required_columns: ["err_sentence", "cor_sentence"]
      note: "여기에 학습 데이터 배치"
```

---

# 🚨 절대 규칙: UV 환경 필수 사용

**모든 Python 명령은 반드시 `uv run` 사용!**
```bash
# ✅ 올바른 실행
uv run python baseline_generate.py

# ❌ 절대 금지 (시스템 Python)
python baseline_generate.py
```

상세 가이드: `/docs/UV_ENVIRONMENT_GUIDE.md`

---

# 🚀 Quick Start

## 필수 체크리스트
```yaml
setup_checklist:
  step1_uv_install:
    status: "required"
    command: "curl -LsSf https://astral.sh/uv/install.sh | sh"
    skip_if: "이미 설치되어 있는 경우"
    
  step2_dependencies:
    status: "required"
    command: "uv sync"
    
  step3_api_key:
    status: "required"
    file: ".env"
    example: "UPSTAGE_API_KEY=your_actual_api_key_here"
    obtain_from: "https://console.upstage.ai/"
    security_note: ".env는 .gitignore에 포함되어 Git에 커밋되지 않음"
    
  step4_data:
    status: "required"
    file: "data/train_dataset.csv"
    required_columns: ["err_sentence", "cor_sentence"]
    
  step5_generate:
    status: "ready"
    command: "uv run python baseline_generate.py"
    
  step6_evaluate:
    status: "ready"
    command: "uv run python evaluate.py"
```

---

# ⚙️ 환경 설정

## 1. uv 설치
```bash
# uv가 설치되어 있지 않은 경우에만 실행
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 2. 의존성 설치
```bash
uv sync
```

## 3. API 키 설정

**.env 파일 생성:**
```bash
# .env.example을 복사하여 .env 생성
cp .env.example .env
```

**.env 파일 내용:**
```
UPSTAGE_API_KEY=your_actual_api_key_here
```

**API 키 발급:**
- URL: https://console.upstage.ai/
- 발급 후 `.env` 파일에 입력

**보안 주의:**
- `.env` 파일은 `.gitignore`에 포함됨
- 절대 Git에 커밋하지 말 것

---

# 📊 데이터 준비

## 필수 파일

**data/train_dataset.csv**
```yaml
required_columns:
  err_sentence:
    description: "교정이 필요한 원문"
    type: "string"
    example: "오늘 날씨가 않좋은데"
    
  cor_sentence:
    description: "교정된 정답 (평가 시 사용)"
    type: "string"
    example: "오늘 날씨가 안 좋은데"
```

---

# 🔧 실행 방법

## 교정 문장 생성

### 기본 실행
```bash
uv run python baseline_generate.py
```

### 옵션 지정
```bash
uv run python baseline_generate.py \
  --input data/train_dataset.csv \
  --output submission.csv \
  --model solar-pro2
```

### 생성 결과

**submission.csv**
```yaml
columns:
  err_sentence:
    description: "원문"
    source: "input file"
    
  cor_sentence:
    description: "AI가 교정한 문장"
    source: "model prediction"
```

---

## 평가 실행

### 기본 실행
```bash
uv run python evaluate.py
```

### 옵션 지정
```bash
uv run python evaluate.py \
  --true_df data/train_dataset.csv \
  --pred_df submission.csv \
  --output analysis.csv
```

### 평가 결과

**콘솔 출력:**
- Recall 점수
- Precision 점수

**analysis.csv:**
- 샘플별 상세 분석
- TP/FP/FN/FR 판정
- 오류 유형별 통계

---

# 🎯 성능 개선 가이드

## 프롬프트 수정 (핵심)

**파일:** `prompts.py`  
**수정 대상:** `baseline_prompt` 변수

### 현재 베이스라인 프롬프트
```python
baseline_prompt = (
"""
# 지시
- 다음 규칙에 따라 원문을 교정하세요.
- 맞춤법, 띄어쓰기, 문장 부호, 문법을 자연스럽게 교정합니다.
- 어떤 경우에도 설명이나 부가적인 내용은 포함하지 않습니다.
- 오직 교정된 문장만 출력합니다.

# 예시
<원문>
오늘 날씨가 않좋은데, 김치찌게 먹으러 갈려고.
<교정>
오늘 날씨가 안 좋은데, 김치찌개 먹으러 가려고.

# 교정할 문장
<원문>
{text}
<교정>
"""
    .strip()
)
```

---

## 실험 전략
```yaml
improvement_strategies:
  
  strategy1_few_shot:
    name: "Few-shot 예시 추가"
    method: "다양한 오류 유형의 예시를 프롬프트에 추가"
    examples:
      - type: "조사오류"
        before: "않은 모습을 처음으로"
        after: "않은 모습이 처음으로"
      - type: "맞춤법"
        before: "금세"
        after: "금세"
      - type: "띄어쓰기"
        before: "읽고있다"
        after: "읽고 있다"
    expected_improvement: "오류 유형별 정확도 향상"
  
  strategy2_error_types:
    name: "오류 유형 명시"
    method: "교정해야 할 오류 유형을 명시적으로 나열"
    prompt_addition: |
      다음 오류를 중점적으로 확인하세요:
      1. 조사 오류 (을/를, 이/가)
      2. 맞춤법 오류
      3. 띄어쓰기 오류
      4. 단순 오타
    expected_improvement: "특정 오류 유형 Recall 증가"
  
  strategy3_cot:
    name: "Chain-of-Thought (단계별 사고)"
    method: "단계별 사고 과정을 유도하는 프롬프트 작성"
    prompt_structure: |
      1단계: 오류 유형 파악
      2단계: 교정 방법 결정
      3단계: 최종 교정 문장 출력
    expected_improvement: "복잡한 오류 처리 능력 향상"
  
  strategy4_multi_turn:
    name: "Multi-turn 검증"
    method: "2단계 검증 프로세스"
    steps:
      - turn1: "오류 탐지"
      - turn2: "교정 실행 및 검증"
    expected_improvement: "False Negative 감소"
```

---

# 📈 평가 메트릭

## 지표 정의
```yaml
metrics:
  TP:
    name: "True Positive"
    definition: "정답과 예측이 모두 같은 위치에서 같은 교정을 수행"
    impact: "positive"
    
  FP:
    name: "False Positive"
    definition: "예측이 잘못된 교정을 수행"
    impact: "negative"
    
  FN:
    name: "False Negative (False Missing)"
    definition: "예측이 필요한 교정을 놓침"
    impact: "negative"
    penalty: "Recall 하락의 주요 원인"
    
  FR:
    name: "False Redundant"
    definition: "예측이 불필요한 교정을 수행"
    impact: "negative"
```

## 계산 공식
```python
# Recall (재현율) - 순위 결정 지표
Recall = TP / (TP + FP + FN) × 100

# Precision (정밀도) - 참고용
Precision = TP / (TP + FP + FR) × 100
```

---

# 🔄 실험 워크플로우

## 추천 프로세스
```yaml
experiment_workflow:
  
  step1_baseline:
    action: "베이스라인 성능 측정"
    commands:
      - "uv run python baseline_generate.py"
      - "uv run python evaluate.py"
    log: "baseline_results.txt"
    
  step2_modify:
    action: "prompts.py 수정"
    target: "baseline_prompt"
    strategies: ["few_shot", "error_types", "cot"]
    
  step3_test:
    action: "수정된 프롬프트 테스트"
    commands:
      - "uv run python baseline_generate.py --output submission_v2.csv"
      - "uv run python evaluate.py --pred_df submission_v2.csv"
    
  step4_compare:
    action: "성능 비교"
    metrics: ["Recall", "Precision"]
    decision: "Recall이 높은 버전 선택"
    
  step5_iterate:
    action: "반복 개선"
    note: "step2-4를 반복하여 최적 프롬프트 도출"
```

---

# 📝 프롬프트 수정 예시

## 예시 1: Few-shot 추가
```python
baseline_prompt = """
# 지시
맞춤법, 띄어쓰기, 문장 부호, 문법을 교정하세요.
오직 교정된 문장만 출력합니다.

# 예시
<원문>감자기 침대에서 일어났다
<교정>갑자기 침대에서 일어났다

<원문>그는 책을 읽고있다
<교정>그는 책을 읽고 있다

<원문>오늘 날씨가 않좋은데
<교정>오늘 날씨가 안 좋은데

# 교정할 문장
<원문>{text}
<교정>
""".strip()
```

## 예시 2: 오류 유형 명시
```python
baseline_prompt = """
# 지시
다음 오류 유형을 중점적으로 확인하고 교정하세요:
1. 조사 오류 (을/를, 이/가, 은/는)
2. 맞춤법 오류 (않/안, 되/돼)
3. 띄어쓰기 오류 (복합어, 보조용언)
4. 단순 오타

교정된 문장만 출력하세요.

# 교정할 문장
<원문>{text}
<교정>
""".strip()
```

## 예시 3: Chain-of-Thought
```python
baseline_prompt = """
# 지시
단계별로 사고하며 문장을 교정하세요.

1단계: 오류 유형 파악 (맞춤법/띄어쓰기/조사/오타)
2단계: 각 오류에 대한 교정 방법 결정
3단계: 최종 교정 문장 출력

반드시 최종 교정 문장만 출력하세요.

# 교정할 문장
<원문>{text}
<교정>
""".strip()
```

---

# 🛠️ 문제 해결

## 자주 발생하는 문제
```yaml
troubleshooting:
  
  issue1_api_key:
    problem: "API 키 오류"
    symptoms: ["Authentication failed", "Invalid API key"]
    solutions:
      - ".env 파일 존재 확인"
      - "UPSTAGE_API_KEY 값 확인"
      - "https://console.upstage.ai/ 에서 키 재발급"
  
  issue2_file_not_found:
    problem: "데이터 파일 없음"
    symptoms: ["FileNotFoundError", "No such file"]
    solutions:
      - "data/train_dataset.csv 존재 확인"
      - "파일 경로 확인"
      - "--input 옵션으로 경로 지정"
  
  issue3_dependencies:
    problem: "패키지 설치 오류"
    symptoms: ["ModuleNotFoundError", "Import error"]
    solutions:
      - "uv sync 재실행"
      - "Python 버전 확인 (.python-version)"
      - "context7 MCP 도구 사용 (의존성 문제)"
  
  issue4_low_recall:
    problem: "Recall 점수가 낮음"
    analysis:
      - "FN (놓친 교정) 수치 확인"
      - "analysis.csv에서 놓친 오류 패턴 분석"
    solutions:
      - "Few-shot 예시 추가"
      - "오류 유형 명시"
      - "Multi-turn 검증 적용"
```

---

# 📊 성능 분석 방법

## analysis.csv 활용
```yaml
analysis_columns:
  err_sentence: "원문"
  cor_sentence_true: "정답"
  cor_sentence_pred: "예측"
  judgment: "판정 (TP/FP/FN/FR)"
  error_type: "오류 유형"
  
usage:
  find_patterns:
    method: "FN 판정된 샘플 필터링"
    purpose: "놓친 오류 패턴 파악"
    action: "해당 패턴에 대한 Few-shot 예시 추가"
  
  error_type_analysis:
    method: "오류 유형별 정확도 계산"
    purpose: "취약한 오류 유형 식별"
    action: "해당 유형에 특화된 프롬프트 작성"
```

---

# ✅ 제출 전 체크리스트
```yaml
submission_checklist:
  code:
    - [ ] prompts.py 최종 버전 확인
    - [ ] baseline_generate.py 실행 성공
    - [ ] submission.csv 생성 확인
  
  evaluation:
    - [ ] evaluate.py 실행 성공
    - [ ] Recall 점수 확인
    - [ ] analysis.csv 검토
  
  documentation:
    - [ ] 실험 로그 기록
    - [ ] 프롬프트 변경 사항 문서화
    - [ ] 최종 성능 지표 기록
  
  security:
    - [ ] .env 파일 Git에 포함되지 않음 확인
    - [ ] API 키 노출 여부 확인
```

---

# 🎓 Best Practices
```yaml
best_practices:
  
  experimentation:
    - "한 번에 하나의 전략만 변경하여 효과 측정"
    - "모든 실험 결과를 로그로 기록"
    - "베이스라인 대비 개선율 추적"
  
  prompt_engineering:
    - "명확하고 구체적인 지시사항 작성"
    - "Few-shot 예시는 다양한 오류 유형 포함"
    - "불필요한 설명 요구하지 않기 (교정 문장만)"
  
  code_management:
    - "prompts.py 버전 관리 (v1, v2, v3...)"
    - "각 버전의 성능 기록"
    - "최고 성능 버전을 final로 저장"
```

---