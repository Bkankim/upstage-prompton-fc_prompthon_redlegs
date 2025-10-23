# Clean 버전 LB 제출 가이드

## 발견된 문제

기존 LB 제출 파일에 형식 오류가 포함되어 있었습니다:

| 프롬프트 | 원본 LB 점수 | 형식 오류 개수 | 형식 오류 비율 |
|---------|-------------|--------------|---------------|
| **Baseline** | 34.04% | 10개 | 9.1% |
| **Few-shot v2** | 31.91% | 24개 | **21.8%** |

Few-shot v2가 Baseline보다 **2.4배 더 많은 형식 오류**를 포함하고 있었습니다!

---

## Clean 버전 생성 완료

모든 형식 오류를 제거한 Clean 버전을 생성했습니다:

### 1. Baseline Clean
- **파일**: `outputs/submissions/test/submission_baseline_test_clean.csv`
- **변경**: 10개 문장 (9.1%)
- **상태**: ✓ 모든 형식 오류 제거 완료

### 2. Few-shot v2 Clean
- **파일**: `outputs/submissions/test/submission_fewshot_v2_test_clean.csv`
- **변경**: 24개 문장 (21.8%)
- **상태**: ✓ 모든 형식 오류 제거 완료

---

## 제출 권장 순서

### Option A: 두 파일 모두 제출 (추천)
1. **Baseline Clean** 먼저 제출
   - 예상: 34.04% 이상 (형식 오류 제거 효과)
2. **Few-shot v2 Clean** 제출
   - 예상: 31.91% 이상 (더 큰 개선 가능)

### Option B: Few-shot v2 Clean만 제출
- 형식 오류가 많았던 Few-shot v2의 개선 효과가 더 클 것으로 예상
- Baseline은 이미 9.1%만 오류여서 개선 폭이 작을 수 있음

---

## 예상 결과

### 시나리오 1: 형식 오류가 주요 원인
- Baseline Clean: 34.04% → **35~36%** (약간 상승)
- Few-shot v2 Clean: 31.91% → **34~36%** (크게 상승)

이 경우 **과적합이 아니라 형식 오류가 주요 원인**이었음을 의미합니다.

### 시나리오 2: 과적합이 주요 원인
- Baseline Clean: 34.04% → **34~35%** (약간 상승)
- Few-shot v2 Clean: 31.91% → **32~33%** (약간 상승, 여전히 Baseline보다 낮음)

이 경우 **과적합이 여전히 주요 원인**임을 의미합니다.

### 시나리오 3: 복합 원인
- Baseline Clean: 34.04% → **35%**
- Few-shot v2 Clean: 31.91% → **34%**

형식 오류와 과적합 모두 영향을 미쳤을 가능성.

---

## 제출 후 해야 할 일

### 1. 결과 기록
```json
{
  "baseline_clean_lb": {
    "recall": ???,
    "precision": ???,
    "vs_original": {
      "recall_diff": ???,
      "note": "형식 오류 제거 효과"
    }
  },
  "fewshot_v2_clean_lb": {
    "recall": ???,
    "precision": ???,
    "vs_original": {
      "recall_diff": ???,
      "note": "형식 오류 제거 효과"
    }
  }
}
```

### 2. 분석 업데이트
- 과적합 분석 보고서 업데이트
- 형식 오류의 영향도 정량화
- 최종 결론 재작성

### 3. 다음 전략 결정
- Few-shot v2 Clean이 Baseline Clean을 넘으면: Few-shot 전략 계속
- 여전히 Baseline이 우수하면: Chain-of-Thought 또는 Baseline 강화

---

## 일일 제출 제한 주의

- 일일 제출 제한: **20회** (KST 자정 리셋)
- 현재까지 제출: Baseline (1회), Few-shot v2 (1회)
- 남은 제출 횟수: **18회**

Clean 버전 2개 제출 후 남은 횟수: **16회**

---

## 중요 포인트

1. **형식 오류 제거의 중요성**
   - Few-shot v2는 21.8%의 문장에 형식 오류
   - 이것만으로도 2~3%p 점수 하락 가능

2. **과적합 vs 형식 오류 구분**
   - Clean 버전 결과로 명확히 구분 가능
   - 과학적 실험 디자인

3. **다음 실험 방향 결정**
   - Clean 결과에 따라 전략 수정
   - 데이터 기반 의사결정

---

**지금 바로 Clean 버전을 LB에 제출하세요!**

파일 위치:
- `code/outputs/submissions/test/submission_baseline_test_clean.csv`
- `code/outputs/submissions/test/submission_fewshot_v2_test_clean.csv`
