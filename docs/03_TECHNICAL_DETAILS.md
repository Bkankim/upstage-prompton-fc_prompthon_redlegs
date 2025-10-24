# 기술 구현 상세

> 아키텍처, 평가 지표, 고급 기법 설명

## 아키텍처 개요

### 전체 흐름

```
Input: 오류 문장
  ↓
[Prompt Template] (System + User + Few-shot)
  ↓
[Upstage Solar Pro 2 API] (최대 3회 호출)
  ↓
[Postprocessor] (메타데이터 제거, 선택적)
  ↓
[Evaluator] (LCS 기반 Recall 계산)
  ↓
Output: 교정 문장 + 메트릭
```

### 핵심 컴포넌트

#### 1. Generator (`src/generator.py`)

```python
class Generator:
    """
    프롬프트를 사용해 교정 문장을 생성하는 클래스
    """
    def generate(self, prompt_class, data: pd.DataFrame) -> List[str]:
        # 1. 프롬프트 인스턴스 생성
        # 2. 각 케이스별로 API 호출 (최대 3회)
        # 3. 응답 정제 (메타데이터 제거 시도)
        # 4. 결과 반환
```

**특징:**
- API 호출 제한: 케이스당 최대 3회 (대회 규칙)
- 토큰 제한: 세션당 2000 토큰
- 에러 핸들링: API 오류 시 원문 반환

#### 2. Prompt Templates (`src/prompts/`)

```python
class BasePrompt:
    """
    모든 프롬프트의 기본 클래스
    """
    def get_prompt(self, err_sentence: str) -> dict:
        """
        Upstage API 형식에 맞는 프롬프트 반환

        Returns:
            {
                "messages": [
                    {"role": "system", "content": "..."},
                    {"role": "user", "content": "..."}
                ]
            }
        """
        raise NotImplementedError
```

**프롬프트 변형:**

| 클래스 | 예시 개수 | 특징 | 성능 |
|--------|-----------|------|------|
| **BaselinePrompt** | 1개 | 다양한 오류 유형 포함 | **34.04%** [완료] |
| ZeroShotPrompt | 0개 | 예시 없음, 보수적 | 31.91% |
| BaselinePlus3ExamplesPrompt | 4개 | 과적합 발생 | 27.66% [실패] |
| BaselineJosaPrompt | 1개 | 조사 특화, 일반화 실패 | 31.91% [실패] |

#### 3. Evaluator (`src/metrics/evaluator.py`)

```python
class Evaluator:
    """
    Longest Common Subsequence (LCS) 기반 평가
    """
    def evaluate(self, true_df: pd.DataFrame, pred_df: pd.DataFrame) -> dict:
        """
        Returns:
            {
                "recall": float,      # TP / (TP + FP + FN) × 100
                "precision": float,   # TP / (TP + FP) × 100
                "tp": int,
                "fp": int,
                "fn": int
            }
        """
```

#### 4. Postprocessor (`src/postprocessors/`)

**MinimalRulePostprocessor** (Phase 6 실험):
```python
class MinimalRulePostprocessor:
    """
    초보수적 규칙 후처리기
    - 원문 = Baseline 출력일 때만 적용
    """
    rules = [
        ("금새", "금세"),
        (r"([가-힣]+)치\s+(않[가-힣]*)", r"\1지 \2"),
        ("추측컨대", "추측건대")
    ]
```

**결과**: 규칙 적용 0개 (Baseline이 이미 모두 처리)

---

## 평가 지표 구현

### Recall 계산 (LCS 기반)

**정의**:
```
Recall = TP / (TP + FP + FN) × 100

TP (True Positive): 정답과 예측이 일치하는 어절
FP (False Positive): 예측에만 있는 어절 (잘못 추가)
FN (False Negative): 정답에만 있는 어절 (놓침)
```

**구현** (`src/metrics/lcs.py`):

```python
def calculate_lcs_recall(true_sentence: str, pred_sentence: str) -> tuple:
    """
    LCS (Longest Common Subsequence) 알고리즘으로 TP/FP/FN 계산

    1. 정답과 예측을 어절 단위로 분리
    2. LCS로 공통 어절 찾기 (TP)
    3. 예측에만 있는 어절 = FP
    4. 정답에만 있는 어절 = FN

    Returns:
        (tp, fp, fn)
    """
    true_words = true_sentence.strip().split()
    pred_words = pred_sentence.strip().split()

    # LCS 계산 (DP)
    lcs_length = compute_lcs(true_words, pred_words)

    tp = lcs_length
    fp = len(pred_words) - tp
    fn = len(true_words) - tp

    return tp, fp, fn
```

**예시**:
```
정답: "오늘 날씨가 안 좋은데"  (5 어절)
예측: "오늘 날씨가 매우 좋은데" (5 어절)

공통 (TP): "오늘", "날씨가", "좋은데" = 3
예측 전용 (FP): "매우" = 1
정답 전용 (FN): "안" = 1

Recall = 3 / (3 + 1 + 1) = 3/5 = 60%
Precision = 3 / (3 + 1) = 3/4 = 75%
```

### Precision vs Recall

**Precision**: 예측의 정확도
```
Precision = TP / (TP + FP) × 100
```

**Recall**: 정답의 재현율
```
Recall = TP / (TP + FP + FN) × 100
```

**대회 목표**: Recall 최대화 (FN 최소화)

**트레이드오프**:
- 공격적 교정 → Recall ↑, Precision ↓
- 보수적 교정 → Recall ↓, Precision ↑

**Baseline 전략**: 공격적 교정 (Recall 우선)

---

## 프롬프트 설계 원칙

### 1. System Message

```python
system_message = """당신은 한국어 문법 전문가입니다.
주어진 문장의 오류를 교정해주세요.

교정 대상:
- 맞춤법, 띄어쓰기
- 문법, 조사
- 문장부호
- 표준어

출력 형식: 교정된 문장만 출력 (메타데이터 없음)
"""
```

**핵심**:
- 역할 명시 (한국어 문법 전문가)
- 교정 대상 나열 (명확성)
- 출력 형식 제약 (메타데이터 방지)

### 2. Few-shot 예시 설계

**좋은 예시 (Baseline)**:
```python
examples = [{
    "err": "오늘 날씨가 않좋은데, 김치찌게 먹으러 갈려고.",
    "cor": "오늘 날씨가 안 좋은데, 김치찌개 먹으러 가려고."
}]

# 포함 오류:
# - 맞춤법: 않→안, 찌게→찌개
# - 띄어쓰기: 않좋은→안 좋은
# - 문법: 갈려고→가려고
```

**나쁜 예시 (Plus3)**:
```python
examples = [
    {"err": "...", "cor": "..."},  # 짧은 문장만
    {"err": "...", "cor": "..."},  # 띄어쓰기 없음
    {"err": "...", "cor": "..."},  # 문장부호 없음
    {"err": "...", "cor": "..."}   # 단순 패턴만
]

# 문제:
# - 모두 짧은 단일 문장 → 긴 문장 처리 실패
# - 띄어쓰기/문장부호 없음 → 해당 오류 소홀
```

**설계 원칙**:
1. **다양성 > 특화**: 단일 예시에 여러 오류 유형
2. **적절한 길이**: 짧지도 길지도 않게
3. **자연스러움**: 실제 사용 가능한 문장
4. **명확한 오류**: 100% 확실한 교정

### 3. 출력 형식 제약

**문제**: 메타데이터 출력 (Baseline 5개 케이스)
```
# 최종 출력
교정된 문장입니다.

[수정 보완]
더 좋은 교정 문장입니다.

최종 출력:
최종 교정 문장입니다.
```

**시도한 해결책**:
1. System message에 명시: "교정된 문장만 출력"
2. RuleChecklist postprocessor (정규식 제거)

**결과**: 부분적 성공 (일부 메타데이터 잔존)

**근본 해결책** (시도 안 함):
- JSON 구조화 출력 강제
- 정규식 검증 추가

---

## 고급 프롬프트 기법 (시도하지 않음)

### Chain-of-Thought (CoT)

```python
system_message = """단계별 사고 과정을 거쳐 교정하세요:
1. 오류 식별
2. 교정 방안 검토
3. 최종 교정 출력
"""
```

**기대 효과**: 복잡한 오류 처리 개선
**리스크**: 토큰 증가, 메타데이터 출력 위험

### Multi-turn

```python
# Turn 1: 오류 탐지
user: "오류를 찾아주세요: {err_sentence}"
assistant: "발견된 오류: ..."

# Turn 2: 교정
user: "이제 교정해주세요."
assistant: "{cor_sentence}"
```

**기대 효과**: 정확도 향상
**리스크**: API 호출 2배, 토큰 증가

### JSON 출력

```python
system_message = """다음 JSON 형식으로만 출력:
{
  "corrected": "교정된 문장"
}
"""
```

**기대 효과**: 메타데이터 완전 제거
**리스크**: 파싱 오류 가능성

---

## 성능 최적화

### 1. API 호출 최적화

**제약사항**:
- 케이스당 최대 3회 호출
- 세션당 2000 토큰

**전략**:
- Few-shot 예시 최소화 (1-2개)
- 간결한 System message
- 배치 처리 (불가, API 제약)

### 2. 후처리 최적화

**RuleChecklist**:
```python
patterns = [
    r"#+\s*최종.*출력",       # "# 최종 출력" 제거
    r"\[.*?(수정|보완).*?\]",  # "[수정 보완]" 제거
    r"최종\s*출력\s*:",        # "최종 출력:" 제거
]
```

**한계**: 정규식으로 모든 패턴 커버 불가

**MinimalRulePostprocessor**:
- 100% 확실한 규칙만
- Baseline 출력 유지 (원문 = Baseline일 때만)
- 길이 가드 (60-150%)

**결과**: 규칙 적용 0개 (이미 처리됨)

### 3. 메모리 최적화

```python
# 배치 처리 대신 스트리밍
for idx, row in data.iterrows():
    result = generate_single(row)
    yield result  # 메모리 효율적
```

---

## 테스트 전략

### 단위 테스트 (85개)

```bash
# 전체 테스트
uv run pytest tests/ -v

# 커버리지
uv run pytest tests/ --cov=src --cov-report=html
```

**테스트 범위**:
- Prompt 템플릿: `tests/test_prompts.py`
- Evaluator 로직: `tests/test_evaluator.py`
- Generator 동작: `tests/test_generator.py`
- Postprocessor: `tests/test_postprocessors.py`

### 통합 테스트

```python
# scripts/run_experiment.py
def test_full_pipeline():
    # 1. 프롬프트 로드
    # 2. Train 데이터 교정
    # 3. 평가 실행
    # 4. Test 데이터 교정
    # 5. 결과 저장
```

---

## 에러 핸들링

### API 오류

```python
try:
    response = api_client.chat(prompt)
except Exception as e:
    logger.error(f"API Error: {e}")
    return err_sentence  # 원문 반환 (안전)
```

### 파싱 오류

```python
def extract_corrected(response: str) -> str:
    # 메타데이터 제거 시도
    cleaned = remove_metadata(response)

    # 실패 시 원본 반환
    if not cleaned or len(cleaned) < 5:
        return response

    return cleaned
```

### 길이 가드

```python
def check_length_guard(original: str, corrected: str) -> bool:
    ratio = len(corrected) / len(original)
    if ratio < 0.6 or ratio > 1.5:
        logger.warning(f"Length anomaly: {ratio}")
        return False
    return True
```

---

## 참고 자료

### 코드

- Generator: `code/src/generator.py`
- Evaluator: `code/src/metrics/evaluator.py`
- LCS 구현: `code/src/metrics/lcs.py`
- Baseline 프롬프트: `code/src/prompts/baseline.py`

### 문서

- 실험 인사이트: [02_EXPERIMENT_INSIGHTS.md](./02_EXPERIMENT_INSIGHTS.md)
- 대회 정보: [04_COMPETITION_GUIDE.md](./04_COMPETITION_GUIDE.md)

### 외부 자료

- Upstage API 문서: https://console.upstage.ai/docs
- LCS 알고리즘: https://en.wikipedia.org/wiki/Longest_common_subsequence_problem

---

**작성일**: 2025-10-24
**대상**: 기술 구현 상세 이해
