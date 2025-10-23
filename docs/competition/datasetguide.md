# 데이터셋 가이드

## 파일 구조
```
data/
├── train_dataset.csv          # 학습 데이터 (254개)
├── test.csv                   # 테스트 데이터 (109개)
└── sample_submission.csv      # 제출 샘플
```

---

## 1. 학습 데이터 (train_dataset.csv)

**254개 문장 | 5개 컬럼**

| 컬럼명 | 설명 | 예시 |
|--------|------|------|
| `type` | 오류 유형 | 조사오류, 맞춤법, 비문, 단순오탈자 등 |
| `original_target_part` | 원본 문장의 오류 부분 | "않은 모습을 처음으로" |
| `golden_target_part` | 교정되어야 할 부분 | "않은 모습이 처음으로" |
| `original` | 오류가 있는 전체 문장 | 전체 원문 |
| `corrected` | 교정된 전체 문장 | 전체 교정문 |

**오류 유형 8종:**
- 조사오류, 맞춤법, 비문, 사이시옷, 논리오류, 문법-품사에따른활용, 단순오탈자, 중복

---

## 2. 테스트 데이터 (test.csv)

**109개 문장 | 2개 컬럼**

| 컬럼명 | 설명 |
|--------|------|
| `id` | 고유 식별자 (grm924197 형식) |
| `err_sentence` | 오류가 있는 문장 |

**Public/Private 분할:**
- Public: 43개 (40%) - 대회 중 실시간 채점
- Private: 66개 (60%) - 대회 종료 후 최종 순위

---

## 3. 제출 파일 (sample_submission.csv)

**109개 문장 | 3개 컬럼**

| 컬럼명 | 설명 | 수정 여부 |
|--------|------|----------|
| `id` | test.csv의 id | 수정 금지 |
| `err_sentence` | test.csv의 err_sentence | 수정 금지 |
| `cor_sentence` | 교정된 문장 (예측 결과) | **여기만 수정** |

---

## 컬럼 매핑
```
train_dataset.csv              test.csv              submission.csv
─────────────────             ─────────            ──────────────
original          →           err_sentence    →    err_sentence
corrected         →           (예측 필요)     →    cor_sentence
```

---

## 데이터 로딩 코드
```python
import pandas as pd

# 데이터 로딩
train_df = pd.read_csv("data/train_dataset.csv")
test_df = pd.read_csv("data/test.csv")
sample_submission = pd.read_csv("data/sample_submission.csv")

print(f"Train: {train_df.shape}")      # (254, 5)
print(f"Test: {test_df.shape}")        # (109, 2)
print(f"Submission: {sample_submission.shape}")  # (109, 3)
```

---

## 제출 전 체크리스트

- [ ] submission.csv 파일명 확인
- [ ] 총 109개 행 (헤더 제외)
- [ ] id 순서가 test.csv와 동일
- [ ] err_sentence 그대로 유지
- [ ] cor_sentence에 실제 예측값 입력
- [ ] UTF-8 인코딩 확인

---

## 주의사항

1. **컬럼명 불일치 주의**
   - Train에서는 `original`/`corrected`
   - Test에서는 `err_sentence`
   - Submission에서는 `err_sentence`/`cor_sentence`

2. **제출 시**
   - `id`, `err_sentence`는 절대 수정 금지
   - `cor_sentence`만 예측값으로 채우기

3. **Public 과적합 주의**
   - Public 리더보드는 40%만 반영
   - Private(60%)가 최종 순위 결정

---

**데이터 출처:** 업스테이지 고객사 데이터 기반 LLM 합성 데이터셋