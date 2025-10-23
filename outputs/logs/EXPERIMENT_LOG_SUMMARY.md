# 실험 로그 요약 (Experiment Log Summary)

> 전체 실험 히스토리 및 성능 비교 스냅샷

**최종 업데이트**: 2025-10-23 (전문가 조언 반영)

---

## 1) 현재 상태 요약

### 최고 성능
- **프롬프트**: Baseline (Response Cleaning 적용)
- **Public LB**: 34.0426%
- **Private LB**: 13.4454%
- **파일**: `submission_baseline_test_clean.csv`
- **특징**: 일반화 우수, 안정적

### 진행 중
- **개선 버전**: 콜론 버그 수정 + 문법 규칙 복원
- **Train Recall**: 33.88%
- **Train Precision**: 15.34%
- **상태**: LB 제출 대기 중
- **파일**: `baseline_test.csv`

### 주요 이슈
⚠️ **Public/Private 격차**: 약 20%p (34.04% vs 13.45%)
  - 일반적 격차: 5-10%p
  - 추정 원인: 데이터 분포 차이
  - 대응 계획: 5-fold 교차검증 + 유형별 분석

### 다음 목표 (전문가 조언 기반)
- **즉시 (오늘)**: 규칙 검증 + 길이 가드 + LB 제출
- **단기 (내일)**: 교차검증 + 프롬프트 형식 제약
- **중기 (모레)**: 일반화 전략 수립 + 통합 개선
- **목표**: Public 35-36%, Private 14-15% (격차 축소)

---

## 2) 전체 실험 결과

| # | 프롬프트 | Train Recall | Public LB | Private LB | Train-Public 격차 | 상태 | 날짜 |
|---|---------|--------------|-----------|------------|------------------|------|------|
| 1 | **Baseline** | 32.24% | **34.04%** | **13.45%** | +1.80%p | ✅ 최고 | 2025-10-22 |
| 2 | Few-shot v2 | **35.92%** | 31.91% | 12.10% | -4.01%p | ❌ 과적합 | 2025-10-22 |
| 3 | Error Types v3 | 32.24% | - | - | ? | 🔄 보류 | 2025-10-22 |
| 4 | Baseline Clean | 32.24% | 34.04% | 13.45% | +1.80%p | ✅ 검증 | 2025-10-23 |
| 5 | Few-shot v2 Clean | 35.92% | 31.91% | 12.10% | -4.01%p | ❌ 검증 | 2025-10-23 |
| 6 | Rule-Checklist (버그) | 33.88% | 31.91% | 12.80% | -1.97%p | ❌ 콜론 버그 | 2025-10-23 |
| 7 | **Rule-Checklist (개선)** | 33.88% | ? | ? | ? | 🔄 제출 대기 | 2025-10-23 |

### 주요 발견
- **Public/Private 격차**: 모든 실험에서 ~20%p 차이 발생
- **콜론 버그**: "7:3" → "3" 변환으로 83% 텍스트 손실 (8개 케이스)
- **문법 규칙 효과**: 41개 케이스 변경, 순효과 미검증

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

## 5) 다음 실험 계획 (전문가 조언 기반)

### 우선순위 A: 즉시 실행 (오늘)

#### 1. 규칙별 순효과 분석 ⚡ 최우선
```yaml
목적: 문법 규칙 유지/제거 근거 확보
파일: code/analyze_grammar_rule_effects.py
입력: outputs/version_comparison.csv (41건)
분석:
  - "되/돼" 규칙: TP vs FP 계산
  - "보조용언 띄어쓰기": TP vs FP 계산
  - "의존명사 띄어쓰기": TP vs FP 계산
출력: outputs/analysis/grammar_rule_effects.csv
판단:
  - 순효과 > 0: 유지
  - 순효과 < 0: 제거
  - 순효과 = 0: 프롬프트 힌트로 대체
예상 시간: 1-2시간
```

#### 2. 60% 길이 가드 구현 ⚡ 긴급
```yaml
목적: 과도한 텍스트 손실 방지 (83% 손실 재발 방지)
파일: code/src/postprocessors/rule_checklist.py
구현:
  - _apply_postprocessing_with_guard() 함수
  - 원문 대비 60% 미만 시 원문 반환
  - 경고 로그 출력
테스트: code/test_length_guard.py
예상 시간: 30분-1시간
```

#### 3. 개선 버전 LB 제출
```yaml
목적: 콜론 버그 수정 효과 검증
파일: outputs/baseline_test.csv
예상:
  - Public: ~34% (기존 최고 유지)
  - Private: ~13.5-14% (콜론 버그 수정 효과)
조건: 규칙 분석 + 길이 가드 완료 후
```

---

### 우선순위 B: 중기 실행 (내일)

#### 4. 5-fold 교차검증
```yaml
목적: 성능 분산 측정, Private 격차 원인 규명
파일: code/analyze_cross_validation.py
방법:
  - Train 254개 → 5-fold (각 ~50개)
  - 각 fold별 Recall/Precision 측정
  - Mean ± Std 계산
분석:
  - Private 13.45%가 95% CI 범위 내인가?
  - 범위 밖이면 "데이터 분포 차이" 확정
출력: outputs/analysis/cross_validation_results.json
예상 시간: 2-3시간
```

#### 5. 유형별 성과 분석
```yaml
목적: 취약 오류 유형 식별
파일: code/analyze_error_type_performance.py
분석:
  - 각 오류 유형별 Recall/Precision
  - 평균 - 1σ 이하 유형 식별
  - Private에서 취약할 가능성 높은 유형 추정
출력: outputs/analysis/error_type_performance.csv
예상 시간: 1-2시간
```

#### 6. 프롬프트 형식 제약 A/B
```yaml
목적: 메타데이터 출력 억제
샘플: 20개 (train.csv)
비교:
  - Version A (현재): 기본 프롬프트
  - Version B (개선): "콜론 금지, 한 문장만, 설명 금지"
측정:
  - 메타데이터 출현 빈도
  - Recall/Precision 변화
파일: code/prompt_ab_test.py
예상 시간: 1-2시간
```

---

### 우선순위 C: 추후 검토 (모레 이후)

#### 7. JSON 형태 실험
```yaml
조건: 프롬프트 A/B 완료 후
목적: 메타데이터 완전 제거
형식: {"output": "교정된 문장"}
리스크: 파싱 오류 시 Recall 급락
샘플: 20개
상태: 보류
```

#### 8. Multi-turn 프로토타입
```yaml
조건: 프롬프트 최적화 완료 후
목적: False Negative 감소
구조:
  - Turn 1: 오류 탐지 (JSON)
  - Turn 2: 교정 실행
  - Turn 3: 검증 (선택)
리스크: 토큰 2000 제약, API 3회 소진
샘플: 30개
상태: 보류
```

#### 9. 고급 프롬프트 기법 (CD-CoT, ToT 등)
```yaml
조건: 기본 파이프라인 안정화 후
목적: 성능 한계 돌파
전제: 일반화 문제 해결이 우선
상태: 장기 검토
```

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

## 7) 성능 향상 로드맵 (전문가 조언 기반)

```
현재: Public 34.04%, Private 13.45% (20%p 격차!)
 ↓
[오늘] 규칙 검증 + 길이 가드
  - 부정적 규칙 제거
  - 과도한 손실 방지
  - 예상: 안정성 확보
 ↓
[내일] 교차검증 + 유형 분석
  - 격차 원인 규명
  - 취약 유형 식별
  - 예상: 전략 방향 확정
 ↓
[모레] 프롬프트 최적화
  - 형식 제약 강화
  - 메타데이터 억제
  - 예상: +1-2%p → Public 35-36%
 ↓
[단기] 일반화 전략
  - 유형별 균형 개선
  - Few-shot 재설계
  - 예상: Private 14-15% (격차 15%p로 축소)
 ↓
[중기] 고급 기법 (조건부)
  - Multi-turn, JSON 형태 등
  - 조건: 기본 파이프라인 안정화 후
  - 예상: +2-3%p 추가 개선
 ↓
목표: Public 35-36%, Private 14-15% (격차 20%p 이하)
      → 일관성 있는 성능 확보!
```

### 우선순위 변경 사항
```diff
- ❌ 기존: CD-CoT, ToT 등 고급 기법 우선
+ ✅ 변경: 기본 안정화 + 일반화 우선

이유:
1. Public/Private 격차(20%p)가 더 심각한 문제
2. 고급 기법은 일반화 문제 해결 후 적용
3. 규칙 검증, 길이 가드 등 기본 안정성 우선
4. 교차검증으로 방향성 확정 필요
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
- `docs/advanced/EXPERT_ADVICE_STRATEGY.md`: **전문가 조언 기반 개선 전략** ⭐ NEW
- `docs/advanced/ADVANCED_STRATEGIES.md`: 2024-2025 최신 기법
- `docs/advanced/EXPERIMENT_LESSONS.md`: 과적합 분석 및 교훈
- `outputs/logs/submission_guide.md`: 제출 전략

### 상세 분석
- `outputs/logs/overfitting_analysis_final.md`: 과적합 심층 분석
- `outputs/logs/final_conclusion.md`: Clean 버전 검증
- `outputs/logs/strategy_shift.md`: 전략 전환
- `outputs/version_comparison.csv`: **버전 비교 (41건 차이)** ⭐ NEW
- `code/analyze_colon_patterns.py`: **콜론 버그 분석** ⭐ NEW

### 콜론 버그 관련
- `code/compare_versions.py`: 버전 비교 도구
- `code/analyze_colon_patterns.py`: 콜론 패턴 분석
- `code/analyze_grammar_rules_effect.py`: 문법 규칙 효과 분석
- `code/test_improved_logic.py`: 개선 로직 검증

### Task 관리
- `tasks/tasks-prd-gec-prompt-optimization-system.md`: 전체 Task 리스트
- `tasks/prd-rule-validation-guard.md`: **규칙 검증 및 가드 PRD** (예정)

---

## 10) 빠른 명령어

### 오늘 즉시 실행
```bash
# 1. 규칙별 순효과 분석
cd code
uv run python analyze_grammar_rule_effects.py

# 2. 60% 길이 가드 테스트
uv run python test_length_guard.py

# 3. 개선 버전 교정 실행 (필요 시)
uv run python scripts/run_experiment.py --prompt baseline

# 결과 확인
cat outputs/analysis/grammar_rule_effects.csv
```

### 내일 실행
```bash
# 4. 5-fold 교차검증
uv run python analyze_cross_validation.py

# 5. 유형별 성과 분석
uv run python analyze_error_type_performance.py

# 6. 프롬프트 A/B 실험
uv run python prompt_ab_test.py

# 결과 확인
cat outputs/analysis/cross_validation_results.json
cat outputs/analysis/error_type_performance.csv
```

### LB 제출 파일 확인
```bash
# 최고 성능 파일
cat outputs/submissions/test/submission_baseline_test_clean.csv

# 개선 버전 파일 (콜론 버그 수정)
cat outputs/baseline_test.csv

# "7:3" 패턴 보존 확인
grep "7:3" outputs/baseline_test.csv
```

---

**핵심 메시지**:
- 기본 안정화 우선 (규칙 검증 + 길이 가드)
- 일반화 문제 해결 (교차검증 + 유형 분석)
- Public/Private 격차 축소 (20%p → 15%p 이하)
- 목표: 일관성 있는 성능 확보!