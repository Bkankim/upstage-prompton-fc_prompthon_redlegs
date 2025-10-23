# 전략 전환 분석: Agent Spec 기반 시스템 개선

## 1. 전문가 스펙 타당성 검증 결과

### 1.1 3-Expert Tree-of-Thought 시스템
**타당성: ✅ 매우 타당함**

현재 시스템의 문제점:
- 단일 프롬프트로 모든 작업 처리 → 복잡한 오류 놓침
- Few-shot v2 과적합: Train 35.92% → LB 31.91% (-4.01%p)

3-Expert 시스템의 해결책:
- **Expert A (Detector)**: 오류 탐지만 집중 → 높은 재현율
- **Expert B (Corrector)**: 탐지된 오류만 교정 → 정확한 수정
- **Expert C (Referee)**: 과교정 방지 + 규칙 적용 → 품질 보증

예상 효과: **+5-7%p Recall 향상**

### 1.2 Rule-Checklist 후처리
**타당성: ✅ 즉시 적용 가능**

국립국어원 근거의 명확한 규칙:
```python
# 즉시 적용 가능한 규칙들
1. '되요' → '돼요' (되서 → 돼서)
2. '할수있다' → '할 수 있다' (의존 명사 '수')
3. '해보다' → '해 보다' (보조 용언)
4. '안돼' → '안 돼' (동사 부정)
```

예상 효과: **즉시 +2-3%p Recall 향상**

### 1.3 Self-Consistency 디코딩
**타당성: ✅ 일반화 성능 향상**

현재 문제점:
- 단일 생성으로 노이즈에 취약
- 일관성 없는 교정 결과

해결책:
- 3-5개 후보 생성 (temperature 조절)
- 다수결로 안정적 결과 선택

예상 효과: **+3-4%p 안정성 향상**

### 1.4 Self-Refine 반복 검증
**타당성: ✅ API 제한 내 실용적**

구현 방안:
- Critic이 구체적 위반사항 지적
- 최대 2회 반복 (API 3회 제한 고려)
- "OK" 반환 시 조기 종료

예상 효과: **+1-2%p 품질 향상**

### 1.5 Reflexion 메모
**타당성: ⚠️ 과적합 위험 존재**

주의사항:
- Train 특화 패턴 기록 시 과적합 위험
- 일반 규칙만 메모하도록 제한 필요

권고: **선택적 구현**

## 2. 주요 변경사항

### 2.1 Tasks 문서 수정 완료
- Task 2.3: Chain-of-Thought → **Rule-Checklist 후처리** (최우선)
- Task 2.4: Multi-turn → **3-Expert ToT 시스템**
- Task 2.5: 신규 → **Self-Refine 반복 검증**
- Task 2.6: 신규 → **Self-Consistency 앙상블**

### 2.2 우선순위 재조정
1. **즉시 구현 (30분-1시간)**
   - Rule-Checklist 후처리
   - 모든 기존 프롬프트에 적용

2. **단기 구현 (2-4시간)**
   - 3-Expert ToT 시스템
   - Self-Consistency 디코딩

3. **중기 구현 (4-6시간)**
   - 통합 파이프라인
   - API 최적화

### 2.3 성공 기준 현실화
- 기존: Recall 75% (비현실적)
- 수정:
  - 단기: 45% (현재 34.04% → +11%p)
  - 중기: 50% (통합 시스템)
  - 장기: 60% (최적화)

## 3. 구현 로드맵

### Phase 1: Rule-Checklist (즉시 시작)
```python
# code/src/utils/rule_checklist.py
def apply_rule_checklist(text):
    """국립국어원 기반 규칙 적용"""
    rules = [
        (r'되요(?![가-힣])', '돼요'),
        (r'되서(?![가-힣])', '돼서'),
        (r'([가-힣])수있', r'\1 수 있'),
        (r'해보([았었])', r'해 보\1'),
        (r'안돼(?![다])', '안 돼'),
    ]
    for pattern, replacement in rules:
        text = re.sub(pattern, replacement, text)
    return text
```

### Phase 2: 3-Expert ToT
```python
# code/src/prompts/three_experts_tot.py
class ThreeExpertToT:
    def detect_errors(self, text):
        """Expert A: 오류 탐지"""
        pass

    def correct_errors(self, text, errors):
        """Expert B: 교정 실행"""
        pass

    def validate_and_refine(self, original, corrected):
        """Expert C: 검증 및 규칙 적용"""
        pass
```

### Phase 3: Self-Consistency
```python
# code/src/utils/self_consistency.py
def self_consistency_decode(prompt, n_samples=3, temp=0.2):
    """다수결 기반 안정적 생성"""
    candidates = [generate(prompt, temp) for _ in range(n_samples)]
    return most_common(candidates)
```

## 4. 예상 성능 개선

| 단계 | 전략 | 현재 Recall | 예상 개선 | 목표 Recall |
|------|------|------------|----------|------------|
| 0 | Baseline | 34.04% | - | 34.04% |
| 1 | + Rule-Checklist | 34.04% | +2-3%p | **36-37%** |
| 2 | + 3-Expert ToT | 36-37% | +5-7%p | **41-44%** |
| 3 | + Self-Consistency | 41-44% | +3-4%p | **44-48%** |
| 4 | + Self-Refine | 44-48% | +1-2%p | **45-50%** |

## 5. API 최적화 전략

### Option 1: Sequential (안전)
```
1회차: Expert A (Detect)
2회차: Expert B (Correct)
3회차: Expert C (Validate)
```

### Option 2: Merged (효율적)
```
1회차: All Experts (통합 프롬프트)
2회차: Self-Refine Round 1
3회차: Self-Refine Round 2
```

### Option 3: Hybrid (권장)
```
1회차: Expert A + B (탐지+교정)
2회차: Expert C + Self-Consistency
3회차: Self-Refine (필요시)
```

## 6. 위험 관리

### 과적합 방지
- Train 특화 규칙 최소화
- 일반 문법 원칙 중심
- 균형 잡힌 오류 유형 처리

### API 초과 방지
```python
class APICounter:
    def __init__(self, max_calls=3):
        self.calls = 0
        self.max_calls = max_calls

    def can_call(self):
        return self.calls < self.max_calls

    def increment(self):
        self.calls += 1
        if self.calls > self.max_calls:
            raise Exception("API 호출 제한 초과")
```

### 품질 체크포인트
- 각 단계별 Recall 측정
- 과교정 모니터링
- 의미 보존 검증

## 7. 다음 단계 액션

### 즉시 실행 (30분 이내)
1. [ ] `utils/rule_checklist.py` 구현
2. [ ] Baseline에 Rule-Checklist 적용
3. [ ] 성능 측정 및 LB 제출

### 오늘 내 완료 (2-4시간)
4. [ ] 3-Expert ToT 기본 구현
5. [ ] Expert 프롬프트 작성
6. [ ] 통합 파이프라인 테스트

### 내일 목표 (4-6시간)
7. [ ] Self-Consistency 구현
8. [ ] Self-Refine 통합
9. [ ] 전체 시스템 최적화

## 8. 결론

agent_spec_gec_ko.md의 전략은:
1. **현재 시스템의 근본적 한계 해결**
2. **즉시 적용 가능한 실용적 방법**
3. **명확한 성능 향상 경로 제시**

특히 Rule-Checklist는 30분 내 구현 가능하면서도 즉시 +2-3%p 성능 향상이 예상되므로, **지금 바로 시작해야 합니다.**

예상 최종 성능:
- 현재: 34.04% (Baseline)
- 목표: **45-50%** (통합 시스템)
- 향상: **+11-16%p**

이는 단순 개선이 아닌 **패러다임 전환**입니다.