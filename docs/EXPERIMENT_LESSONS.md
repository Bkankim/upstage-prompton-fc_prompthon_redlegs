# 실험 교훈 및 베스트 프랙티스

> Few-shot v2 과적합 사례 분석 및 일반화 전략

## 0) Executive Summary

**핵심 발견**: Few-shot v2는 Train에서 35.92%로 우수했으나, LB에서 31.91%로 하락 (-4.01%p 과적합)

**주요 원인**:
1. Few-shot 예시가 Train의 상위 3개 오류 유형만 커버 (52%)
2. 나머지 48% 오류 유형은 예시 부족으로 성능 저하
3. Train 특화 패턴 학습

**해결책**: 일반화 중심 전략 (CD-CoT, 3-Expert ToT, Rule-Checklist)

---

## 1) 과적합 사례 분석: Few-shot v2

### 1.1 성능 비교

| 프롬프트 | Train Recall | LB Recall | 격차 | 일반화 |
|---------|-------------|-----------|------|--------|
| Baseline | 32.24% | **34.04%** | +1.80%p | ✅ 우수 |
| Few-shot v2 | **35.92%** | 31.91% | -4.01%p | ❌ 과적합 |
| Error Types v3 | 32.24% | ? | ? | ? |

### 1.2 과적합 증거 5가지

#### 증거 1: Train/LB 성능 역전
- Train: Few-shot v2 (35.92%) > Baseline (32.24%) → **+3.68%p**
- LB: Baseline (34.04%) > Few-shot v2 (31.91%) → **-2.13%p**
- **총 격차**: 5.81%p

#### 증거 2: Few-shot 예시의 편향된 커버리지
```python
# Few-shot v2의 6개 예시 분석
few_shot_coverage = {
    "조사오류": 2,  # 33.3% (Train 16.1%)
    "표준어비표준어": 1,  # 16.7% (Train 9.4%)
    "사이시옷": 1,  # 16.7% (Train 13.4%)
    "능동피동": 1,  # 16.7%
    "문법-품사": 1,  # 16.7%
    "기타 15개 유형": 0  # 0%!
}

# 커버리지 분석
covered_samples = 132 / 254  # 52%
uncovered_samples = 122 / 254  # 48%
```

**문제점**: 예시 없는 오류 유형(48%)은 성능 저하 예상

#### 증거 3: 오류 유형별 성능 차이

```python
# Few-shot v2 대비 Baseline 성능 차이
error_type_performance = {
    # Few-shot v2가 우수한 유형 (예시 有)
    "맞춤법-맞춤법": +12.82%p,
    "문법-품사": +14.58%p,
    "표준어비표준어": +8.18%p,
    "사이시옷": +5.69%p,

    # Few-shot v2가 저조한 유형 (예시 無)
    "문장부호-문장부호": -4.11%p,  # 예시 0개
    # ... 기타 예시 없는 유형들
}
```

#### 증거 4: Baseline의 일관된 성능
- Train 32.24% → LB 34.04% (+1.80%p)
- 오히려 LB에서 더 좋은 성능 (일반화 우수)

#### 증거 5: Clean 버전 검증
- 형식 오류 제거 후에도 Recall 변화 없음 (0%p)
- Precision만 소폭 상승 (+0.2~0.5%p)
- **과적합이 실제 원인임을 확인**

---

## 2) 형식 오류 분석

### 2.1 형식 오류 유형

```python
# 발견된 형식 오류
format_errors = {
    "태그 오류": "<교정> ... </교정>",
    "설명 오류": "(※ ... )",
    "줄바꿈": "\n",
}

# 발생 빈도
baseline_test_errors = 10 / 109  # 9.1%
fewshot_v2_test_errors = 24 / 109  # 21.8%
```

### 2.2 형식 오류 영향 분석

| 프롬프트 | 원본 Recall | Clean Recall | 차이 |
|---------|------------|-------------|------|
| Baseline | 34.04% | 34.04% | 0%p |
| Few-shot v2 | 31.91% | 31.91% | 0%p |

| 프롬프트 | 원본 Precision | Clean Precision | 차이 |
|---------|---------------|----------------|------|
| Baseline | 13.22% | 13.44% | +0.22%p |
| Few-shot v2 | 10.79% | 11.28% | +0.49%p |

**결론**: 형식 오류는 Precision에만 소폭 영향, **Recall에는 영향 없음**

### 2.3 Clean 버전 생성 코드

```python
import re
import pandas as pd

def clean_correction_v2(text):
    """
    형식 오류 제거 (개선된 버전)
    - <교정> 태그 제거
    - (※ ... ) 설명 제거
    - ※ 단독 설명 제거
    - 줄바꿈 정리
    """
    if pd.isna(text):
        return text

    # <교정> 태그 제거
    text = re.sub(r'<교정>\s*', '', text)

    # (※ ... ) 괄호형 설명 제거
    text = re.sub(r'\(※[^)]*\)', '', text)

    # ※ 단독 설명 제거 (괄호 없는 경우)
    text = re.sub(r'※[^\n]*', '', text)

    # 줄바꿈을 공백으로 변환
    text = text.replace('\n', ' ')

    # 여러 공백을 하나로
    text = re.sub(r'\s+', ' ', text)

    # 앞뒤 공백 제거
    text = text.strip()

    return text
```

---

## 3) 전략 전환: Train 최적화 → 일반화

### 3.1 기존 전략 (Few-shot v2)

```python
# 문제가 있던 접근
strategy_old = {
    "목표": "Train Recall 최대화",
    "방법": "Train 상위 오류 유형 Few-shot 예시",
    "결과": "Train 35.92%, LB 31.91% (과적합)"
}
```

### 3.2 새로운 전략 (일반화 중심)

```python
# 개선된 접근
strategy_new = {
    "목표": "LB Recall 최대화 (일반화 성능)",
    "방법": "보편적 규칙 + Robust 프롬프팅",
    "기법": [
        "Contrastive Denoising (CD-CoT)",
        "3-Expert ToT",
        "Rule-Checklist",
        "Self-Consistency"
    ],
    "원칙": [
        "Train 특화 규칙 지양",
        "모든 오류 유형 균등 처리",
        "명확한 오류만 수정 (보수적 접근)",
        "의미 보존 최우선"
    ]
}
```

### 3.3 일반화 전략 체크리스트

```
일반화 프롬프트 설계 원칙:

□ Train 데이터 특정 패턴을 하드코딩하지 않았는가?
□ 모든 오류 유형에 균등하게 적용되는가?
□ 보편적 문법 규칙(국립국어원 기준)만 사용하는가?
□ 불확실한 경우 원문을 유지하는가?
□ 의미/어조/문체를 보존하는가?
□ Few-shot 예시 없이도 작동하는가?
```

---

## 4) 베스트 프랙티스

### 4.1 ✅ DO - 권장 사항

#### 1. 보수적 교정 접근
```python
# 좋은 예: 명확한 오류만 수정
if is_clear_error(text):
    correct(text)
else:
    keep_original(text)
```

#### 2. 보편적 규칙 사용
```python
# 좋은 예: 국립국어원 규칙
rules = {
    "되요": "돼요",  # 명확한 규칙
    "할수있다": "할 수 있다",  # 의존 명사
}
```

#### 3. 의미 보존 최우선
```python
# 좋은 예: 최소 편집
before = "나는 학교에 갔어요"
after = "나는 학교에 갔어요"  # 오류 없으면 그대로

# 나쁜 예: 불필요한 변경
before = "나는 학교에 갔어요"
after = "저는 학교에 다녀왔습니다"  # ❌ 어조 변경
```

#### 4. 균형 잡힌 커버리지
```python
# 좋은 예: 모든 오류 유형 처리
error_types = get_all_error_types()  # 20개 유형
for error_type in error_types:
    apply_general_rule(error_type)

# 나쁜 예: 특정 유형만 집중
focus_only_on = ["조사오류", "표준어"]  # ❌ 편향
```

### 4.2 ❌ DON'T - 피해야 할 사항

#### 1. Train 특화 규칙
```python
# 나쁜 예: Train 데이터 특정 패턴
if text in train_frequent_errors:  # ❌
    apply_specific_fix()
```

#### 2. 과도한 교정
```python
# 나쁜 예: 불필요한 변경
before = "좀 어려워요"
after = "조금 어렵습니다"  # ❌ 어조 변경
```

#### 3. 불균형 예시
```python
# 나쁜 예: 편향된 Few-shot
examples = [
    조사오류_예시,
    조사오류_예시,  # 같은 유형 반복
    조사오류_예시,
]  # ❌ 다른 유형 무시
```

---

## 5) 실험 설계 가이드

### 5.1 Train/LB 분할 전략

```python
# 권장: 교차 검증
from sklearn.model_selection import StratifiedKFold

# 오류 유형별 계층화 분할
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
for train_idx, val_idx in skf.split(X, y_error_types):
    train_set = data.iloc[train_idx]
    val_set = data.iloc[val_idx]

    # 검증: 오류 유형 분포 확인
    assert train_set['type'].value_counts(normalize=True).corr(
        val_set['type'].value_counts(normalize=True)
    ) > 0.9  # 높은 상관관계
```

### 5.2 일반화 성능 측정

```python
# Train과 LB 격차 모니터링
def generalization_gap(train_recall, lb_recall):
    gap = lb_recall - train_recall
    if gap < -3.0:
        return "과적합 의심"
    elif gap > 3.0:
        return "과소적합 의심"
    else:
        return "양호"

# 예시
baseline_gap = 34.04 - 32.24  # +1.80%p → 양호
fewshot_gap = 31.91 - 35.92  # -4.01%p → 과적합
```

### 5.3 실험 우선순위

```python
experiment_priority = [
    {
        "name": "Rule-Checklist",
        "risk": "낮음",  # 과적합 위험 낮음
        "roi": "높음",  # 즉시 효과
        "priority": 1
    },
    {
        "name": "CD-CoT",
        "risk": "낮음",  # 일반화 기법
        "roi": "매우 높음",  # +10-15%p
        "priority": 2
    },
    {
        "name": "Few-shot",
        "risk": "높음",  # 과적합 위험
        "roi": "중간",
        "priority": 9  # 최후 수단
    }
]
```

---

## 6) 다음 실험 방향

### 6.1 즉시 적용 (오늘)

1. **Rule-Checklist 후처리**
   - 위험: 낮음
   - 예상: +2-3%p
   - 시간: 30분

2. **Contrastive Denoising (CD-CoT)**
   - 위험: 낮음 (일반화 기법)
   - 예상: +10-15%p
   - 시간: 2시간

### 6.2 단기 실험 (1-2일)

3. **3-Expert Tree-of-Thought**
   - 위험: 낮음 (체계적 접근)
   - 예상: +5-7%p
   - 시간: 2시간

4. **Self-Consistency**
   - 위험: 낮음 (다수결)
   - 예상: +3-4%p
   - 시간: 1시간

### 6.3 회피할 접근

```python
# 피해야 할 실험들
avoid_experiments = [
    "Train 데이터 암기형 Few-shot",
    "특정 오류 유형만 집중",
    "과도한 프롬프트 엔지니어링 (Train 맞춤)",
    "의미 변경하는 공격적 교정"
]
```

---

## 7) 교훈 요약

### 핵심 인사이트 10가지

1. **Train 성능 ≠ LB 성능**: 일반화가 핵심
2. **Few-shot의 양날검**: 편향된 예시는 과적합 유발
3. **보수적 교정의 중요성**: 불확실하면 원문 유지
4. **균형 잡힌 커버리지**: 모든 오류 유형 균등 처리
5. **형식 오류는 Recall에 무관**: Precision에만 소폭 영향
6. **Baseline의 우수한 일반화**: 단순함의 힘
7. **CD-CoT의 높은 잠재력**: 2024년 +17.8% 검증
8. **3-Expert ToT의 체계성**: 역할 분리로 품질 향상
9. **Rule-Checklist의 안정성**: 명확한 규칙은 항상 유효
10. **Self-Consistency의 안전성**: 다수결로 노이즈 감소

### 실천 가이드

```
즉시 적용:
✓ Rule-Checklist 모든 프롬프트에 추가
✓ CD-CoT 프롬프트 구현
✓ 보수적 교정 원칙 적용

단기 적용:
✓ 3-Expert ToT 시스템 구축
✓ Self-Consistency 통합
✓ 오류 유형별 성능 모니터링

회피:
✗ Train 특화 Few-shot 예시
✗ 특정 유형 편향 프롬프트
✗ 공격적 교정 전략
```

---

## 8) 참고 자료

### 분석 문서
- `code/outputs/logs/overfitting_analysis_final.md`: 과적합 심층 분석
- `code/outputs/logs/final_conclusion.md`: Clean 버전 검증 결과
- `code/outputs/logs/strategy_shift.md`: 전략 전환 방향

### 실험 결과
- `code/outputs/logs/baseline_results.json`: Baseline 성능
- `code/outputs/logs/fewshot_v2_results.json`: Few-shot v2 성능
- `code/outputs/logs/fewshot_v2_lb_results.json`: LB 제출 결과

### 관련 문서
- `docs/ADVANCED_STRATEGIES.md`: 최신 기법 가이드
- `tasks/tasks-prd-gec-prompt-optimization-system.md`: Task 리스트

---

*"과적합은 나쁜 것이 아니라, 일반화로 가는 중요한 교훈이다."*