# 고급 프롬프트 전략 가이드 (Advanced Prompt Strategies)

> 2024-2025 최신 기법 및 전문가 검증 전략 통합 문서

## 0) TL;DR - 빠른 시작

**목표**: 한국어 문법 교정에서 Recall 최대화 (현재 34% → 목표 55-65%)

**핵심 전략 TOP 3**:
1. **Contrastive Denoising (CD-CoT)** - +10-15%p (최고 ROI, 2024년 검증)
2. **3-Expert Tree-of-Thought** - +5-7%p (체계적 접근)
3. **Rule-Checklist 후처리** - +2-3%p (즉시 적용 가능)

**제약사항**:
- API 호출: 케이스당 최대 3회
- 토큰 제한: 세션당 2000 토큰
- 외부 데이터 사용 금지

---

## 1) 2024-2025 최신 프롬프트 기법

### 1.1 Contrastive Denoising with Noisy CoT (CD-CoT) ⭐⭐⭐⭐⭐

**2024년 검증 성과: +17.8% 정확도 향상**

**핵심 아이디어**: 잘못된 교정 예시와 올바른 교정을 대비시켜 노이즈 제거

**구현 방법**:
```python
def contrastive_denoising_prompt(text):
    """
    CD-CoT 프롬프트 생성
    - 잘못된 교정 패턴 제시
    - 올바른 교정 패턴 제시
    - 대비를 통한 학습
    """
    prompt = f"""
당신은 한국어 문법 교정 전문가입니다.

다음 문장을 교정하되, 아래의 잘못된 교정 예시를 피하고 올바른 교정 방법을 따르세요.

원문: "{text}"

[잘못된 교정 예시 - 이렇게 하지 마세요]
❌ 과도한 의역: "나는 학교에 갔다" → "저는 학교에 다녀왔습니다" (어조 변경)
❌ 불필요한 추가: "비가 온다" → "비가 내리고 있습니다" (불필요한 진행형)
❌ 의미 변경: "좀 어렵다" → "매우 어렵다" (강도 변경)

[올바른 교정 예시 - 이렇게 하세요]
✓ 최소 편집: "되요" → "돼요" (명확한 오류만 수정)
✓ 의미 보존: "할수있다" → "할 수 있다" (띄어쓰기만 수정)
✓ 문법 규칙: "안돼요" → "안 돼요" (규칙 기반 수정)

이제 원문을 교정하세요. 반드시 최소 편집 원칙을 지키고, 의미를 보존하세요.

교정된 문장:
"""
    return prompt
```

**예상 효과**: +10-15%p Recall 향상

**API 사용**: 1-2회

---

### 1.2 3-Expert Tree-of-Thought (ToT) ⭐⭐⭐⭐⭐

**검증 성과**: ToT 74% vs CoT 9% 성공률 (Game of 24 문제)

**핵심 아이디어**: 탐지, 교정, 검증을 독립된 전문가로 분리

#### Expert A: Detector (탐지 전문가)

```python
def expert_a_detect(text):
    """
    오류 탐지만 집중
    - JSON 형식으로 의심 오류 리스트 반환
    - 과탐지 허용 (Recall 우선)
    """
    prompt = f"""
당신은 Expert A (오류 탐지 전문가)입니다.

임무: 다음 한국어 문장에서 의심되는 오류만 찾아 JSON으로 출력하세요.
교정하지 말고, 탐지만 하세요.

원문: "{text}"

오류 유형:
- 맞춤법: 띄어쓰기, 사이시옷, 외래어 표기
- 문법: 조사, 어미, 품사, 시제
- 어휘: 표준어, 비표준어, 적절성
- 문장: 중복, 호응, 어순

출력 형식 (JSON):
{{
  "suspected_errors": [
    {{
      "type": "맞춤법-띄어쓰기",
      "span": "할수있다",
      "position": [5, 9],
      "rationale": "'수'는 의존 명사로 반드시 띄어씀",
      "severity": "high"
    }}
  ]
}}

JSON만 출력하세요:
"""
    return prompt
```

#### Expert B: Corrector (교정 전문가)

```python
def expert_b_correct(text, errors_json):
    """
    탐지된 오류만 최소 편집으로 교정
    - Expert A의 JSON 입력 받음
    - 각 오류별 교정안 제시
    """
    prompt = f"""
당신은 Expert B (교정 전문가)입니다.

임무: Expert A가 탐지한 오류를 최소 편집으로 교정하세요.

원문: "{text}"

탐지된 오류:
{errors_json}

교정 원칙:
1. 의미 보존: 원문의 어조, 문체, 뉘앙스 유지
2. 최소 편집: 꼭 필요한 부분만 수정
3. 규칙 기반: 명확한 문법 규칙만 적용

출력 형식 (JSON):
{{
  "corrections": [
    {{
      "before": "할수있다",
      "after": "할 수 있다",
      "reason": "의존 명사 '수' 띄어쓰기 (국립국어원 규칙)",
      "confidence": 0.95
    }}
  ],
  "corrected_text": "전체 교정된 문장"
}}

JSON만 출력하세요:
"""
    return prompt
```

#### Expert C: Referee (검증 전문가)

```python
def expert_c_referee(original, corrected, corrections_json):
    """
    과교정 제거 및 규칙 체크리스트 적용
    - Expert B의 교정 검증
    - 최종 품질 보증
    """
    prompt = f"""
당신은 Expert C (검증 및 심판 전문가)입니다.

임무: Expert B의 교정 결과를 검토하고 최종 승인하세요.

원문: "{original}"
교정안: "{corrected}"
교정 내역:
{corrections_json}

검증 체크리스트:
□ 의미가 보존되었는가?
□ 최소 편집 원칙을 지켰는가?
□ 불필요한 변경이 없는가?
□ 문법 규칙이 올바른가?
□ 과교정(over-correction)이 없는가?

필수 규칙 재확인:
1. '되요/되서' → '돼요/돼서'
2. '할수있다' → '할 수 있다'
3. '해보다' → '해 보다'
4. '안돼' (동사 부정) → '안 돼'

출력 형식 (JSON):
{{
  "final_text": "최종 승인된 교정 문장",
  "rejected_corrections": ["과교정으로 거부된 항목들"],
  "notes": ["최소 편집 유지", "의미 보존 확인", "규칙 준수"]
}}

JSON만 출력하세요:
"""
    return prompt
```

**예상 효과**: +5-7%p Recall 향상

**API 사용**: 1-3회 (병렬 가능)

---

### 1.3 Self-Consistency 앙상블 디코딩 ⭐⭐⭐⭐⭐

**핵심 아이디어**: 여러 추론 경로 생성 후 다수결로 선택

```python
from collections import Counter

def self_consistency_decode(prompt, n_samples=3, temperature=0.2):
    """
    Self-Consistency 디코딩
    - 동일 프롬프트로 n_samples개 생성
    - temperature로 다양성 확보
    - 다수결로 최종 선택
    """
    candidates = []

    for i in range(n_samples):
        # temperature 약간씩 조절하여 다양성 확보
        temp = temperature + (i * 0.05)
        response = generate_with_temperature(prompt, temp)
        candidates.append(response)

    # 가장 빈도 높은 교정 선택
    chosen, count = Counter(candidates).most_common(1)[0]

    # 일치도 계산
    consensus = count / n_samples

    return {
        "final": chosen,
        "consensus": consensus,
        "candidates": candidates
    }
```

**사용 팁**:
- Expert C에만 적용 (API 제한 고려)
- n_samples=3으로 충분
- temperature 0.1-0.3 범위 권장

**예상 효과**: +3-4%p 안정성 향상

**API 사용**: 3회 (SC만 적용 시)

---

### 1.4 Rule-Checklist 후처리 ⭐⭐⭐⭐⭐

**즉시 적용 가능, 국립국어원 규칙 기반**

```python
import re

def apply_rule_checklist(text):
    """
    명확한 규칙 기반 후처리
    - 과교정 방지를 위해 보수적 설계
    - 명백한 오류만 수정
    """
    if not text or pd.isna(text):
        return text

    # (1) '되/돼' 활용: 되요/되서 → 돼요/돼서
    # 국립국어원: "되어요/되어서"의 준말은 "돼요/돼서"
    text = re.sub(r'(?<![가-힣])되요(?![가-힣])', '돼요', text)
    text = re.sub(r'(?<![가-힣])되서(?![가-힣])', '돼서', text)
    text = re.sub(r'되여요', '돼요', text)
    text = re.sub(r'되여서', '돼서', text)

    # (2) '안 돼' 띄어쓰기: 동사 부정은 띄어씀
    text = re.sub(r'안돼요', '안 돼요', text)
    text = re.sub(r'안돼서', '안 돼서', text)
    text = re.sub(r'안된다(?![가-힣])', '안 된다', text)

    # (3) '-ㄹ 수 있다' 띄어쓰기: '수'는 의존 명사
    # '할수있다' → '할 수 있다'
    text = re.sub(r'([가-힣])수(있[다어요습니다])', r'\1 수 \2', text)
    text = re.sub(r'([가-힣])수(없[다어요습니다])', r'\1 수 \2', text)

    # (4) 보조 용언 띄어쓰기: 원칙은 띄어씀
    # '해보다' → '해 보다', '해보았다' → '해 보았다'
    text = re.sub(r'해보([았었엿])', r'해 보\1', text)
    text = re.sub(r'해봐(요)?', r'해 봐\1', text)
    text = re.sub(r'해보자', '해 보자', text)

    # (5) 줄바꿈 및 공백 정리
    text = text.replace('\n', ' ')
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()

    return text
```

**주의사항**:
- 보수적 접근: 명백한 오류만 수정
- 문맥 의존적 규칙은 제외
- 과교정 방지

**예상 효과**: +2-3%p 즉시 향상

**API 사용**: 0회 (후처리)

---

### 1.5 Instance-Adaptive Prompting (IAP) ⭐⭐⭐⭐

**2024년 신규 기법: 각 인스턴스에 맞춤형 프롬프트**

```python
def instance_adaptive_prompt(text, error_type_detector):
    """
    오류 유형별 특화 프롬프트 자동 선택
    - 사전 탐지로 오류 유형 파악
    - 해당 유형 특화 프롬프트 사용
    """
    # 1단계: 빠른 오류 유형 탐지
    error_types = error_type_detector(text)

    # 2단계: 유형별 특화 프롬프트 선택
    if "띄어쓰기" in error_types:
        return spacing_specialized_prompt(text)
    elif "조사" in error_types:
        return particle_specialized_prompt(text)
    elif "맞춤법" in error_types:
        return spelling_specialized_prompt(text)
    else:
        return general_correction_prompt(text)

def spacing_specialized_prompt(text):
    """띄어쓰기 특화 프롬프트"""
    return f"""
당신은 한국어 띄어쓰기 전문가입니다.

문장: "{text}"

띄어쓰기 핵심 규칙:
1. 의존 명사는 반드시 띄어씀: 수, 것, 데, 바, 등
2. 보조 용언은 원칙적으로 띄어씀: -아/어 보다, -아/어 주다
3. 단위명사는 띄어씀: 10 개, 3 명

띄어쓰기만 수정하고, 다른 부분은 변경하지 마세요.

교정:
"""
```

**예상 효과**: +2-3%p 유형별 최적화

**API 사용**: 2회 (탐지 + 교정)

---

### 1.6 Logic-of-Thought (LoT) Prompting ⭐⭐⭐⭐

**2024년 검증: CoT 대비 +4.35%, ToT 대비 +8%**

**핵심 아이디어**: 문법 규칙을 명제 논리로 표현

```python
def logic_of_thought_prompt(text):
    """
    논리 기반 추론 프롬프트
    - 문법 규칙을 IF-THEN 논리식으로 표현
    - 명확한 추론 체인 구성
    """
    prompt = f"""
당신은 논리적 추론 기반 문법 교정 전문가입니다.

문장: "{text}"

논리 규칙 체인:

[규칙 1] 되/돼 구분
- IF: 어미가 '-어요/-어서'로 활용됨
- AND: 어간이 '되-'임
- THEN: '돼요/돼서'로 교정
- 예: "되요" → "돼요" (∵ '되어요'의 준말)

[규칙 2] 의존 명사 띄어쓰기
- IF: 명사 '수/것/데/바' 등이 나타남
- AND: 앞에 관형사형 어미가 있음
- THEN: 반드시 띄어 씀
- 예: "할수" → "할 수" (∵ '수'는 의존 명사)

[규칙 3] 보조 용언 띄어쓰기
- IF: 본용언 뒤 '-아/어'가 나타남
- AND: 뒤에 '보다/주다/버리다/놓다' 등이 나타남
- THEN: 원칙적으로 띄어 씀
- 예: "해보다" → "해 보다"

[규칙 4] 안 부정
- IF: '안' 뒤에 용언이 나타남
- THEN: 띄어 씀
- 예: "안돼" → "안 돼" (∵ 동사 부정)

이제 위 논리 규칙을 순차적으로 적용하여 교정하세요.

추론 과정:
1. 규칙 1 적용 →
2. 규칙 2 적용 →
3. 규칙 3 적용 →
4. 규칙 4 적용 →

최종 교정:
"""
    return prompt
```

**예상 효과**: +4-8%p (논리 기반 정확도)

**API 사용**: 1회

---

## 2) 통합 파이프라인 설계

### 2.1 최적 조합 (API 3회 제한 내)

```python
def integrated_pipeline(text):
    """
    통합 파이프라인: Rule → CD-CoT → ToT → SC
    - API 3회 제한 준수
    - 최대 성능 목표
    """

    # Round 1: Detection + Initial Correction (병합)
    # CD-CoT + Expert A+B 통합
    round1_prompt = f"""
[Contrastive Denoising 원칙]
잘못된 교정 패턴을 피하고, 올바른 교정만 수행하세요.

[Expert A: Detect]
오류를 JSON으로 탐지하세요.

[Expert B: Correct]
탐지된 오류를 최소 편집으로 교정하세요.

원문: "{text}"

출력 (JSON):
{{
  "errors": [...],
  "corrected": "..."
}}
"""
    response1 = call_api(round1_prompt)  # API 1회

    # Round 2: Validation + Self-Consistency (Expert C)
    round2_prompt = f"""
[Expert C: Referee]
다음 교정안을 검증하고 최종 승인하세요.

원문: "{text}"
교정안: "{response1['corrected']}"

3개 버전을 생성하여 가장 일치하는 것을 선택하세요.
"""
    response2 = self_consistency_api(round2_prompt, n=3)  # API 1회 (SC 내장)

    # Round 3: Logic-based Refinement
    round3_prompt = f"""
[Logic-of-Thought 최종 검증]
논리 규칙을 적용하여 최종 검증하세요.

교정안: "{response2['final']}"

논리 규칙 체크:
- 되/돼 규칙 확인
- 의존 명사 띄어쓰기 확인
- 보조 용언 띄어쓰기 확인

최종 교정:
"""
    response3 = call_api(round3_prompt)  # API 3회

    # 후처리: Rule-Checklist 적용
    final = apply_rule_checklist(response3)

    return final
```

### 2.2 대안 파이프라인 (더 보수적)

```python
def conservative_pipeline(text):
    """
    보수적 파이프라인: 일반화 중심
    - 과적합 방지
    - Baseline 대비 안정적 개선
    """

    # Round 1: CD-CoT로 기본 교정
    cd_cot_result = contrastive_denoising_prompt(text)
    response1 = call_api(cd_cot_result)  # API 1회

    # Round 2: 3-Expert ToT 병합 (A+B+C)
    tot_merged = f"""
[Expert A] 오류 탐지
[Expert B] 최소 편집 교정
[Expert C] 과교정 제거

원문: "{text}"
1차 교정: "{response1}"

최종 교정:
"""
    response2 = call_api(tot_merged)  # API 2회

    # Round 3: Rule-Checklist 후처리만
    final = apply_rule_checklist(response2)

    return final
```

---

## 3) 구현 우선순위 로드맵

### Phase 1: 즉시 구현 (30분-1시간)

1. **Rule-Checklist 후처리**
   - 파일: `code/src/utils/rule_checklist.py`
   - 난이도: ⭐ (매우 낮음)
   - ROI: ⭐⭐⭐⭐⭐
   - 예상 효과: +2-3%p

```python
# 즉시 적용 가능한 코드
from src.utils.rule_checklist import apply_rule_checklist

# 모든 프롬프트 결과에 적용
corrected_text = prompt_result
final_text = apply_rule_checklist(corrected_text)
```

### Phase 2: 최우선 구현 (1-2시간)

2. **Contrastive Denoising (CD-CoT)**
   - 파일: `code/src/prompts/cd_cot.py`
   - 난이도: ⭐⭐⭐ (중간)
   - ROI: ⭐⭐⭐⭐⭐ (최고!)
   - 예상 효과: +10-15%p

```python
# 프롬프트 클래스에 추가
class ContrastiveDenoisingCoT(BasePrompt):
    def build_prompt(self, text):
        return contrastive_denoising_prompt(text)
```

### Phase 3: 핵심 아키텍처 (2-4시간)

3. **3-Expert Tree-of-Thought**
   - 파일: `code/src/prompts/three_experts_tot.py`
   - 난이도: ⭐⭐⭐ (중간)
   - ROI: ⭐⭐⭐⭐⭐
   - 예상 효과: +5-7%p

4. **Self-Consistency 디코딩**
   - 파일: `code/src/utils/self_consistency.py`
   - 난이도: ⭐⭐ (낮음)
   - ROI: ⭐⭐⭐⭐
   - 예상 효과: +3-4%p

### Phase 4: 추가 최적화 (4-6시간)

5. **Instance-Adaptive Prompting**
   - 파일: `code/src/prompts/instance_adaptive.py`
   - 난이도: ⭐⭐⭐ (중간)
   - ROI: ⭐⭐⭐⭐
   - 예상 효과: +2-3%p

6. **Logic-of-Thought**
   - 파일: `code/src/prompts/logic_of_thought.py`
   - 난이도: ⭐⭐⭐⭐ (높음)
   - ROI: ⭐⭐⭐⭐
   - 예상 효과: +4-8%p

---

## 4) 성능 향상 예측

### 단계별 누적 효과

| 단계 | 전략 | 예상 Recall | 개선폭 | 검증 근거 |
|------|------|------------|--------|----------|
| 0 | Baseline | 34.04% | - | LB 실측 |
| 1 | + Rule-Checklist | 36-37% | +2-3%p | 국립국어원 규칙 |
| 2 | + CD-CoT | 46-52% | +10-15%p | **2024년 +17.8%** |
| 3 | + 3-Expert ToT | 51-59% | +5-7%p | ToT 74% vs CoT 9% |
| 4 | + Self-Consistency | 54-63% | +3-4%p | 다수결 안정성 |
| 5 | + Instance-Adaptive | 56-66% | +2-3%p | 유형별 최적화 |

### 목표 설정

- **단기 (오늘-내일)**: 50% Recall
  - Rule-Checklist + CD-CoT

- **중기 (2-3일)**: 55% Recall
  - 위 + 3-Expert ToT + Self-Consistency

- **장기 (대회 종료)**: 60-65% Recall
  - 전체 통합 시스템

---

## 5) API 제한 최적화 전략

### 제약사항
- 케이스당 최대 3회 API 호출
- 세션당 2000 토큰

### 최적화 방법

#### 방법 1: 병렬 처리
```python
# Expert A + B를 하나의 프롬프트로 병합
merged_prompt = """
[Expert A] 오류 탐지
[Expert B] 교정 실행
"""
# 1회로 2개 전문가 처리
```

#### 방법 2: Self-Consistency 내장
```python
# Expert C에 SC 기능 내장
prompt = """
[Expert C] 검증하되, 3개 버전 생성 후 다수결
"""
# 1회로 SC까지 처리
```

#### 방법 3: 단계별 캐싱
```python
# 공통 부분은 캐싱
common_rules = load_from_cache("rule_checklist")
# 토큰 절약
```

---

## 6) 과적합 방지 원칙

### 교훈: Few-shot v2 과적합 사례

**문제점**:
- Train 35.92% → LB 31.91% (-4.01%p)
- Few-shot 예시가 Train의 상위 3개 오류 유형만 커버 (52%)
- 나머지 48% 오류 유형은 성능 저하

**해결책**:
1. **일반 원칙 중심**: 특정 예시 대신 보편적 규칙
2. **균형 잡힌 커버리지**: 모든 오류 유형 균등 처리
3. **보수적 교정**: 불확실하면 원문 유지
4. **Contrastive Learning**: CD-CoT로 잘못된 패턴 회피

### 일반화 전략

```python
def generalization_prompt(text):
    """
    일반화 중심 프롬프트
    - Train 특화 규칙 지양
    - 보편적 문법 원칙 적용
    """
    prompt = f"""
당신은 한국어 문법 교정 전문가입니다.

원칙:
1. 명확한 오류만 수정 (불확실하면 원문 유지)
2. 의미 보존 (어조, 문체, 뉘앙스 유지)
3. 최소 편집 (꼭 필요한 부분만)
4. 보편적 규칙 (국립국어원 기준)

문장: "{text}"

교정:
"""
    return prompt
```

---

## 7) 초보자용 빠른 시작 코드

### 7.1 Rule-Checklist 적용 (5분)

```python
# 1. 파일 생성: code/src/utils/rule_checklist.py
import re
import pandas as pd

def apply_rule_checklist(text):
    if not text or pd.isna(text):
        return text

    # 되/돼 규칙
    text = re.sub(r'(?<![가-힣])되요(?![가-힣])', '돼요', text)
    text = re.sub(r'(?<![가-힣])되서(?![가-힣])', '돼서', text)

    # 안 돼 띄어쓰기
    text = re.sub(r'안돼요', '안 돼요', text)

    # 할 수 있다
    text = re.sub(r'([가-힣])수(있[다어요])', r'\1 수 \2', text)

    # 보조 용언
    text = re.sub(r'해보([았었])', r'해 보\1', text)

    return text.strip()

# 2. 사용: 모든 프롬프트 결과에 적용
from src.utils.rule_checklist import apply_rule_checklist

result = generator.generate(text)
final = apply_rule_checklist(result)
```

### 7.2 CD-CoT 프롬프트 적용 (10분)

```python
# 1. 파일 생성: code/src/prompts/cd_cot.py
from src.prompts.base_prompt import BasePrompt

class ContrastiveDenoisingCoT(BasePrompt):
    name = "cd_cot"
    description = "Contrastive Denoising with Noisy CoT"

    def build_prompt(self, text: str) -> dict:
        system = """당신은 한국어 문법 교정 전문가입니다.
잘못된 교정 패턴을 피하고, 올바른 최소 편집 교정만 수행하세요."""

        user = f"""
원문: "{text}"

[잘못된 교정 - 피하세요]
❌ 과도한 의역
❌ 불필요한 추가
❌ 의미 변경

[올바른 교정 - 따르세요]
✓ 최소 편집
✓ 의미 보존
✓ 문법 규칙만

교정:
"""

        return {
            "system": system,
            "user_turns": [{"user": user}]
        }

# 2. 레지스트리 자동 등록 (registry.py가 처리)

# 3. 사용
uv run python scripts/run_experiment.py --prompt cd_cot
```

---

## 8) 참고 문헌

### 전문가 스펙 근거
- 국립국어원 온라인가나다: '되요/돼요', '안 돼', '할 수 있다' 규칙
- 한글 맞춤법: 보조 용언 띄어쓰기

### 2024-2025 최신 연구
- **Contrastive Denoising (CD-CoT)**: 2024년 +17.8% 검증
- **Tree of Thoughts**: Yao et al., 2023 (74% vs 9%)
- **Logic-of-Thought**: 2024년 CoT 대비 +4.35%
- **Instance-Adaptive Prompting**: Yuan et al., 2024
- **Self-Consistency**: Wang et al., ICLR 2023

---

## 9) 다음 단계

### 즉시 시작
1. Rule-Checklist 구현 (30분)
2. 성능 측정 (Baseline + Rule)
3. LB 제출

### 오늘 내 완료
4. CD-CoT 프롬프트 구현 (2시간)
5. 성능 측정 (+ CD-CoT)
6. LB 제출

### 내일 목표
7. 3-Expert ToT 구현
8. Self-Consistency 통합
9. 통합 파이프라인 테스트

**예상 최종 성능**: 55-65% Recall
**현재 대비**: +21-31%p 향상

---

*이 문서는 agent_spec_gec_ko.md, latest_techniques_analysis_2024.md, strategy_update_from_agent_spec.md를 통합하여 작성되었습니다.*