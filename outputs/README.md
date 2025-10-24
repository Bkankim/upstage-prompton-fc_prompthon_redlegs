# 실험 결과

이 디렉토리는 모든 프롬프트 실험의 결과를 포함합니다.

## 디렉토리 구조

```
outputs/
├── submissions/      # 교정 결과 CSV 파일
│   ├── train/        # Train 데이터 교정 결과
│   └── test/         # Test 데이터 교정 결과 (LB 제출용)
├── logs/             # 평가 메트릭 JSON 로그
└── analysis/         # 상세 케이스별 분석 CSV
```

---

## 제출 파일 (submissions/)

### Train 교정 결과 (`submissions/train/`)

Train 데이터(254개)에 대한 교정 결과:

```csv
id,err_sentence,cor_sentence
grm123456,"오류 문장","교정된 문장"
...
```

**주요 파일:**
- `submission_baseline.csv`: Baseline 프롬프트 (최고 성능)
- `submission_zero_shot.csv`: Zero-shot
- `submission_baseline_plus_3examples.csv`: Plus3
- `submission_baseline_josa.csv`: 조사 특화

### Test 제출 파일 (`submissions/test/`)

Test 데이터(109개)에 대한 LB 제출용 파일:

**최종 제출 파일 (4개 사용):**

| 파일 | Public LB | Private LB | 결과 |
|------|-----------|------------|------|
| `submission_baseline_test_clean.csv` | **34.04%** | **13.45%** | [완료] **최고** |
| `submission_zero_shot_test.csv` | 31.91% | 12.61% | [주의] 보수적 |
| `submission_baseline_josa_test.csv` | 31.91% | 11.54% | [실패] 특화 실패 |
| `submission_baseline_plus_3examples_test.csv` | 27.66% | 9.77% | [실패] 과적합 |

**사용 제출**: 4회 / 20회 (16회 남음)

---

## 평가 로그 (logs/)

각 실험의 Recall/Precision 메트릭 JSON 파일:

### 파일 형식

```json
{
  "prompt": "baseline",
  "train_performance": {
    "recall": 32.24,
    "precision": 14.79,
    "tp": 296,
    "fp": 1720,
    "fn": 622
  },
  "timestamp": "2025-10-22T...",
  "total_cases": 254
}
```

### 주요 로그

- `baseline_results.json`: Baseline (Train 32.24%)
- `zero_shot_train_results.json`: Zero-shot (Train 32.24%)
- `baseline_plus_3examples_train_results.json`: Plus3 (Train 34.69%)
- `baseline_josa_train_results.json`: 조사 (Train 33.47%)
- `baseline_minimal_rules_train_results.json`: Phase 6 규칙 후처리 (Train 32.24%)

### 핵심 발견

**Train 성능 ≠ Test 성능:**

| 프롬프트 | Train Recall | Public LB | 격차 |
|---------|--------------|-----------|------|
| Baseline | 32.24% | **34.04%** | +1.80%p (일반화 우수) [완료] |
| Zero-shot | 32.24% | 31.91% | -0.33%p |
| Plus3 | **34.69%** | **27.66%** | **-7.03%p** (과적합) [실패] |
| 조사 | 33.47% | 31.91% | -1.56%p (특화 실패) [실패] |

**교훈**: Train 성능 향상 → Test 성능 하락 (과적합)

---

## 상세 분석 (analysis/)

케이스별 교정 결과 및 비교 CSV 파일:

### 파일 형식

```csv
id,err_sentence,cor_sentence,pred_sentence,length_original,length_pred,tp,fp,fn
grm123456,"오류","정답","예측",10,12,8,4,2
...
```

### 주요 분석 파일

- `FINAL_EXPERIMENT_SUMMARY.md`: Phase 1-5 종합 분석 [중요]
- `FAILURE_ANALYSIS_BASELINE_PLUS_3EXAMPLES.md`: Plus3 실패 상세 분석 [중요]
- `FINAL_MINIMAL_RULES_EXPERIMENT.md`: Phase 6 규칙 후처리 실험 [중요]

**통합 문서**: [docs/02_EXPERIMENT_INSIGHTS.md](../docs/02_EXPERIMENT_INSIGHTS.md)

---

## 실험 이력 요약

### 전체 실험 (Phase 1-6)

| Phase | 프롬프트 | 예시 | Train | Public | Private | 결과 |
|-------|---------|------|-------|--------|---------|------|
| 1 | **Baseline** | **1개** | 32.24 | **34.04** | **13.45** | [완료] **최고** |
| 2 | Zero-shot | 0개 | 32.24 | 31.91 | 12.61 | [주의] 보수적 |
| 2 | Plus3 | 4개 | 34.69 | 27.66 | 9.77 | [실패] 과적합 |
| 3 | 조사 | 1개 (조사) | 33.47 | 31.91 | 11.54 | [실패] 특화 실패 |
| 3 | 띄어쓰기 | 1개 (띄어쓰기) | 32.65 | - | - | [실패] 폐기 (길이 폭발) |
| 6 | 규칙 후처리 | - | 32.24 | - | - | [실패] 규칙 적용 0개 |

### 핵심 발견

1. **Few-shot 최적점**: 1개 예시가 최고 성능
   - 0개: 보수적 → FN 증가
   - 1개: 균형 → 최적
   - 4개: 과적합 → 일반화 실패

2. **예시 다양성 > 특화**
   - 맞춤법 예시(3가지 오류 유형) > 조사 예시(1가지)

3. **Train 성능 무의미**
   - Train 향상 → Test 하락 (모든 실험)

4. **Baseline 강력함**
   - 명확한 규칙은 이미 100% 처리
   - 규칙 추가 시도 → 적용 0개

5. **근본적 한계**
   - Public/Private 격차 20%p (구조적 문제)

---

## 로그 확인 방법

### 단일 실험 결과

```bash
# JSON 로그 확인
cat logs/baseline_results.json

# 보기 좋게 포맷팅
cat logs/baseline_results.json | python -m json.tool
```

### 전체 실험 비교

```bash
# 모든 실험의 Recall 비교
grep -h "recall" logs/*_results.json
```

### 케이스별 상세 분석

```bash
# 특정 케이스 검색
grep "grm123456" analysis/analysis_baseline.csv
```

---

## 제출 파일 생성

### Train 평가용

```bash
cd code
uv run python scripts/run_experiment.py --prompt baseline
```

**결과**:
- `outputs/submissions/train/submission_baseline.csv`
- `outputs/logs/baseline_results.json`

### Test LB 제출용

```bash
cd code
uv run python generate_test_submission.py
```

**결과**:
- `outputs/submissions/test/submission_baseline_test.csv`

---

## 참고 자료

### 프로젝트 문서

- **실험 인사이트**: [../docs/02_EXPERIMENT_INSIGHTS.md](../docs/02_EXPERIMENT_INSIGHTS.md) [중요] 필독
- **기술 상세**: [../docs/03_TECHNICAL_DETAILS.md](../docs/03_TECHNICAL_DETAILS.md)
- **대회 정보**: [../docs/04_COMPETITION_GUIDE.md](../docs/04_COMPETITION_GUIDE.md)

### 코드

- **코드 구조**: [../code/README.md](../code/README.md)
- **프롬프트**: `code/src/prompts/`
- **실험 스크립트**: `code/*.py`

---

**마지막 업데이트**: 2025-10-24
**최종 성과**: Baseline 34.04% Public / 13.45% Private
