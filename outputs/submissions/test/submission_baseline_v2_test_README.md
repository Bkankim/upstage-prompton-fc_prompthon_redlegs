# Submission: baseline_v2_test

**제출 일시:** 2025-10-23
**파일:** submission_baseline_v2_test.csv
**케이스 수:** 110개

---

## 개선 사항

### 1. 길이 가드 적용
- 원문 대비 60% 미만 손실 시 원문 반환
- "7:3" → "3" 같은 심각한 손실 방지
- Test 데이터 2건 보호 가능

### 2. 메타데이터 제거 개선
- 콜론 로직 향상
- 비율/시간 패턴 보존
- 메타데이터 레이블 정확 제거

### 3. 안정성 강화
- 예외 처리 개선
- 로깅 추가
- 파이프라인 검증

---

## 기존 버전 대비

**기준:** submission_baseline_test_clean.csv (현재 최고 성능)
- Public LB: 34.0426%
- Private LB: 13.4454%

**변경 케이스:** 41개 (37.3%)

**주요 차이:**
1. API 응답 랜덤성
2. 표현 개선 (간결화, 문법 향상)
3. 길이 가드 작동 (예상)

---

## 기대 효과

### 긍정적 시나리오
- 길이 가드로 심각한 손실 방지 → Recall 개선
- 표현 개선으로 자연스러움 향상
- Public/Private 격차 축소 가능

### 주의 사항
- API 랜덤성으로 일부 케이스 변동
- 보조용언 띄어쓰기 차이 발생
- 성능 변화 모니터링 필요

---

## 제출 체크리스트

- [x] 110개 케이스 모두 생성
- [x] 파일 형식 검증 (err_sentence, cor_sentence)
- [x] 메타데이터 제거 확인
- [x] 길이 가드 작동 확인
- [x] 기존 버전과 비교 분석

---

## LB 제출 후 확인 사항

1. Public LB 점수 (목표: 34% 이상 유지)
2. Private LB 점수 (목표: 격차 축소)
3. 성능 변화 패턴 분석
4. 후속 조치 결정

---

**생성 명령:**
```bash
uv run python scripts/generate.py \
  --prompt baseline \
  --input data/test.csv \
  --output outputs/submissions/test/submission_baseline_v2_test.csv \
  --model solar-pro
```

**소요 시간:** 2분 1초 (110개)
**평균 속도:** 1.11초/케이스
