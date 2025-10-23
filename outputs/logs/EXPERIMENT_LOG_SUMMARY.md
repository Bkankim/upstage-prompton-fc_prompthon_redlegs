# 실험 로그 요약 (Experiment Log Summary)

> 전체 실험 히스토리 및 성능 비교 스냅샷

**최종 업데이트**: 2025-10-23

---

## 1) 현재 상태 요약

### 최고 성능
- **프롬프트**: Baseline
- **LB Recall**: 34.04%
- **LB Precision**: 13.22%
- **특징**: 일반화 우수, 안정적

### 다음 목표
- **단기 (오늘-내일)**: 50% Recall
  - Rule-Checklist + CD-CoT
- **중기 (2-3일)**: 55% Recall
  - + 3-Expert ToT + Self-Consistency
- **장기 (대회 종료)**: 60-65% Recall

---

## 2) 전체 실험 결과

| # | 프롬프트 | Train Recall | LB Recall | LB Precision | 격차 | 상태 | 날짜 |
|---|---------|--------------|-----------|--------------|------|------|------|
| 1 | **Baseline** | 32.24% | **34.04%** | 13.22% | +1.80%p | ✅ 최고 | 2025-10-22 |
| 2 | Few-shot v2 | **35.92%** | 31.91% | 10.79% | -4.01%p | ❌ 과적합 | 2025-10-22 |
| 3 | Error Types v3 | 32.24% | - | - | ? | 🔄 대기 | 2025-10-22 |
| 4 | Baseline Clean | 32.24% | 34.04% | 13.44% | +1.80%p | ✅ 검증 | 2025-10-23 |
| 5 | Few-shot v2 Clean | 35.92% | 31.91% | 11.28% | -4.01%p | ❌ 검증 | 2025-10-23 |

---

## 3) 주요 인사이트

### ✅ 성공 사례: Baseline
```
Train: 32.24% → LB: 34.04% (+1.80%p)
- 일반화 우수
- 보수적 교정
- 안정적 성능
```

### ❌ 실패 사례: Few-shot v2
```
Train: 35.92% → LB: 31.91% (-4.01%p)
- Train 특화 예시 (상위 3개 유형만)
- 편향된 커버리지 (52%)
- 과적합 발생
```

### 💡 교훈
1. **일반화가 핵심**: Train 성능 ≠ LB 성능
2. **Few-shot 주의**: 편향된 예시는 과적합 유발
3. **보수적 접근**: 불확실하면 원문 유지
4. **균형 커버리지**: 모든 오류 유형 균등 처리

---

## 4) 오류 유형별 성능 (Few-shot v2 vs Baseline)

| 오류 유형 | Baseline | Few-shot v2 | 차이 | 예시 유무 |
|----------|----------|-------------|------|----------|
| 맞춤법-맞춤법 | 25.00% | **37.82%** | +12.82%p | ✅ 有 |
| 문법-품사 | 20.42% | **35.00%** | +14.58%p | ✅ 有 |
| 표준어비표준어 | 26.82% | **35.00%** | +8.18%p | ✅ 有 |
| 사이시옷 | 25.69% | **31.38%** | +5.69%p | ✅ 有 |
| 문장부호-문장부호 | **18.11%** | 14.00% | -4.11%p | ❌ 無 |

**결론**: Few-shot 예시가 있는 유형은 개선, 없는 유형은 저하

---

## 5) 다음 실험 계획

### Phase 1: 즉시 구현 (30분-1시간)
- [ ] Rule-Checklist 후처리
  - 예상: +2-3%p → 36-37% Recall
  - 파일: `utils/rule_checklist.py`

### Phase 2: 최우선 구현 (1-2시간)
- [ ] Contrastive Denoising (CD-CoT)
  - **예상: +10-15%p → 46-52% Recall**
  - 검증: 2024년 +17.8% 성과
  - 파일: `prompts/cd_cot.py`

### Phase 3: 핵심 아키텍처 (2-4시간)
- [ ] 3-Expert Tree-of-Thought
  - 예상: +5-7%p → 51-59% Recall
  - 파일: `prompts/three_experts_tot.py`

- [ ] Self-Consistency
  - 예상: +3-4%p → 54-63% Recall
  - 파일: `utils/self_consistency.py`

---

## 6) 실험 파일 위치

### 프롬프트 코드
```
code/src/prompts/
├── baseline.py          # ✅ 현재 최고
├── fewshot_v2.py        # ❌ 과적합
├── errortypes_v3.py     # 🔄 대기
├── cd_cot.py            # 🆕 개발 예정
└── three_experts_tot.py # 🆕 개발 예정
```

### 제출 파일
```
code/outputs/submissions/test/
├── submission_baseline_test.csv          # LB 34.04%
├── submission_fewshot_v2_test.csv        # LB 31.91%
├── submission_baseline_test_clean.csv    # LB 34.04%
├── submission_fewshot_v2_test_clean.csv  # LB 31.91%
└── (다음 실험 결과들...)
```

### 실험 로그
```
code/outputs/logs/
├── baseline_results.json
├── fewshot_v2_results.json
├── errortypes_v3_results.json
├── fewshot_v2_lb_results.json
└── comparison_*.json
```

---

## 7) 성능 향상 로드맵

```
현재: 34.04% (Baseline)
 ↓
Step 1: +2-3%p → 36-37% (Rule-Checklist)
 ↓
Step 2: +10-15%p → 46-52% (CD-CoT)  ← 게임 체인저!
 ↓
Step 3: +5-7%p → 51-59% (3-Expert ToT)
 ↓
Step 4: +3-4%p → 54-63% (Self-Consistency)
 ↓
목표: 55-65% Recall 달성!
```

---

## 8) 형식 오류 분석

### 발견된 오류
| 프롬프트 | 형식 오류 개수 | 비율 | 영향 |
|---------|--------------|------|------|
| Baseline | 10개 | 9.1% | Precision만 +0.22%p |
| Few-shot v2 | 24개 | 21.8% | Precision만 +0.49%p |

**결론**: 형식 오류는 Recall에 영향 없음 (0%p), 과적합이 실제 원인

---

## 9) 참고 문서

### 전략 가이드
- `docs/ADVANCED_STRATEGIES.md`: 2024-2025 최신 기법
- `docs/EXPERIMENT_LESSONS.md`: 과적합 분석 및 교훈
- `code/outputs/logs/submission_guide.md`: 제출 전략

### 상세 분석
- `code/outputs/logs/overfitting_analysis_final.md`: 과적합 심층 분석
- `code/outputs/logs/final_conclusion.md`: Clean 버전 검증
- `code/outputs/logs/strategy_shift.md`: 전략 전환

### Task 관리
- `tasks/tasks-prd-gec-prompt-optimization-system.md`: 전체 Task 리스트

---

## 10) 빠른 명령어

### 다음 실험 실행
```bash
# Rule-Checklist 적용
uv run python scripts/run_experiment.py --prompt baseline_rulechecklist

# CD-CoT 실험
uv run python scripts/run_experiment.py --prompt cd_cot

# 3-Expert ToT 실험
uv run python scripts/run_experiment.py --prompt three_experts_tot
```

### 결과 확인
```bash
# Train 평가
cat code/outputs/logs/*_results.json | grep recall

# LB 제출 파일 확인
ls -lh code/outputs/submissions/test/*.csv
```

---

**핵심 메시지**: Baseline (34.04%)에서 CD-CoT 적용으로 46-52% 달성 목표!