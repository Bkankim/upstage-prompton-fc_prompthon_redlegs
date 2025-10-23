## Relevant Files

### 핵심 소스 코드 (src/)
- `code/src/prompts/` - 프롬프트 템플릿 모듈 (핵심 수정 대상)
  - `baseline.py` - 베이스라인 프롬프트
  - `fewshot_v2.py` - Few-shot v2 프롬프트
  - `errortypes_v3.py` - Error Types v3 프롬프트
  - `registry.py` - 프롬프트 레지스트리 (자동 등록 및 조회)
- `code/src/generator.py` - 통합 문장 생성기 클래스
- `code/src/evaluator.py` - 평가 클래스
- `code/src/postprocessors/` - 후처리 시스템 (Rule-Checklist 등)
- `code/src/metrics/lcs.py` - LCS 알고리즘
- `code/src/metrics/evaluator.py` - Recall/Precision 계산 로직

### 실행 스크립트 (scripts/)
- `code/scripts/generate.py` - 교정 실행 (통합 스크립트, --prompt 인자로 선택)
- `code/scripts/evaluate.py` - 평가 실행
- `code/scripts/run_experiment.py` - 전체 워크플로우 (교정 + 평가 + LB 제출 파일)
- `code/scripts/verify_setup.py` - 환경 검증 스크립트

### 실험 결과 (outputs/)
- `code/outputs/logs/baseline_results.json` - 베이스라인 성능 (Recall 32.24%)
- `code/outputs/logs/fewshot_v2_results.json` - Few-shot v2 성능 (Recall 35.92%)
- `code/outputs/logs/errortypes_v3_results.json` - Error Types v3 성능 (Recall 32.24%)
- `code/outputs/logs/experiments/` - Phase별 실험 결과 (JSON)
- `code/outputs/logs/comparison_*.json` - 프롬프트 비교 분석
- `code/outputs/submissions/train/` - Train 데이터 교정 결과
- `code/outputs/submissions/test/` - LB 제출 파일
- `code/outputs/analysis/` - 상세 분석 CSV

### 테스트 (tests/)
- `code/tests/test_prompts.py` - 프롬프트 모듈 테스트 (24개)
- `code/tests/test_generator.py` - 생성기 테스트 (17개)
- `code/tests/test_metrics.py` - 메트릭 테스트 (26개)
- `code/tests/test_evaluator.py` - 평가기 테스트 (18개)
- `code/tests/test_postprocessors.py` - 후처리 테스트

### Notes

- **⚠️ 중요: 모든 Python 실행은 반드시 `uv run python` 명령 사용**
- 베이스라인 코드는 이미 `/code` 폴더에 준비되어 있음
- uv를 사용한 의존성 관리 (pyproject.toml)
- Python 3.12 사용 (.python-version)
- 실험은 베이스라인 성능 측정부터 시작하여 점진적으로 개선
- 모든 실험 결과는 JSON 형식으로 로깅
- 상세 uv 가이드: `/docs/UV_ENVIRONMENT_GUIDE.md`

---

## Tasks

### Phase 1: 베이스라인 성능 측정 (완료 ✅)

- [x] 1.0 베이스라인 성능 측정 및 분석
  - [x] 1.1 환경 설정 및 의존성 설치 확인 (uv sync)
  - [x] 1.2 API 키 설정 확인 (.env 파일)
  - [x] 1.3 데이터 파일 배치 확인 (code/data/train_dataset.csv)
  - [x] 1.4 베이스라인 프롬프트로 교정 실행 (scripts/generate.py --prompt baseline)
  - [x] 1.5 베이스라인 Recall 점수 측정 (scripts/evaluate.py)
  - [x] 1.6 오류 유형별 분석 결과 검토 (analysis.csv)
  - [x] 1.7 베이스라인 성능 문서화 (logs/baseline_results.json)

**Phase 1 완료 결과:**
- Train Recall: 32.24%, Precision: 14.95%
- Public LB: 34.0426%, Private LB: 13.4454%
- 과적합 확인: Few-shot v2 (Train 35.92% → LB 31.91%)
- 주요 발견: 콜론 버그 (83% 텍스트 손실), Public/Private 격차 20%p

---

### Phase 2: 기본 안정화 (최우선 ⚡)

**목적**: 규칙 검증 + 텍스트 손실 방지 + 안정된 베이스라인 확보

- [ ] 2.0 프롬프트 개선 전략 실험
  - [x] 2.1 Few-shot 예시 추가 버전 작성 (prompts/fewshot_v2.py)
  - [x] 2.2 오류 유형 명시 버전 작성 (prompts/errortypes_v3.py)

  - [x] 2.3 **Rule-Checklist 후처리 시스템** (src/postprocessors/rule_checklist.py)
    - [x] 2.3.0 콜론 처리 로직 개선 (3단계 검증)
      - [x] 비율/시간 패턴 체크 (7:3, 3:00)
      - [x] 위치 체크 (앞부분 30% 이내)
      - [x] 메타데이터 키워드 체크
      - [x] 검증: test_improved_logic.py 통과

    - [x] 2.3.1 **규칙별 순효과 분석** (analyze_grammar_rule_effects_v2.py)
      - [x] Train 254개 케이스를 규칙 OFF로 재생성
      - [x] 규칙별 TP/FP 계산 및 순효과 측정
      - [x] 결과: API가 이미 문법 규칙을 학습함 (모든 규칙 효과 0)
      - [x] 판단: 규칙 유지 (효과 없지만 해롭지 않음, 안정성 우선)
      - [x] 산출물: `outputs/logs/grammar_rule_analysis_v2.csv`

    - [x] 2.3.2 **60% 길이 가드 구현** (src/postprocessors/rule_checklist.py)
      - [x] Dry-run 영향도 분석 (test_length_guard_impact.py)
        - [x] Train: 0개 롤백 (0.0%)
        - [x] Test: 2개 심각한 손실 방지 가능
      - [x] `_apply_length_guard()` 함수 구현
        - [x] 원문 대비 60% 미만 시 원문 반환
        - [x] 경고 로그 출력 (logger.warning)
      - [x] 단위 테스트: test_length_guard.py (8개 테스트 통과)
        - [x] "7:3이었다" → "3이었다" 방지 확인 ✅
        - [x] 정상 교정 (60% 이상) 통과 확인 ✅

    - [x] 2.3.3 **개선 버전 LB 제출**
      - [x] Test 데이터 교정 (submission_baseline_v2_test.csv)
      - [x] LB 제출 및 결과 기록
      - [x] 결과: Public 31.91%, Private 12.30% (기존 대비 하락)
      - [x] 원인 분석 완료 (API 랜덤성 60%, 메타데이터 제거 불완전 30%)
      - [x] 결정: 기존 최고 버전(34.04%) 유지

    - [x] 2.3.4 **Phase 2 완료 검증**
      - [x] 성능 하락 원인 분석 문서 (performance_drop_root_cause.md)
      - [x] Phase 2 결과 로그: `outputs/logs/phase2_results.md`
      - [x] .gitignore 검증
      - [x] GitHub 동기화 필요

**Phase 2 실제 결과:**
```yaml
기술적 구현: ✅ 완료
  - 규칙 순효과 분석 완료 (API가 이미 학습, 효과 0)
  - 60% 길이 가드 구현 및 테스트 통과 (8개 테스트 ✅)
  - Dry-run 롤백 비율: 0% (Train), 2건 방지 가능 (Test)

성능 목표: ❌ 미달 (API 랜덤성)
  - Public LB: 31.91% (목표 34.5%, -2.6%p)
  - Private LB: 12.30% (목표 14.0%, -1.7%p)
  - 원인: API 랜덤성(60%), 메타데이터 불완전(30%), 분포 차이(10%)

주요 발견:
  - Solar Pro 2 API가 문법 규칙을 이미 학습함
  - 같은 프롬프트라도 호출 시점에 따라 응답 다름
  - Train 성능 개선(+2.14%p) ≠ Test 성능 개선(-2.13%p)
  - 메타데이터 과다 포함 케이스 존재 (grm260797)

산출물:
  ✅ outputs/logs/grammar_rule_analysis_v2.csv
  ✅ outputs/logs/phase2_results.md
  ✅ outputs/logs/performance_drop_root_cause.md
  ✅ test_length_guard.py (8개 테스트)
  ✅ submission_baseline_v2_test.csv (폐기)

교훈:
  1. API 재호출은 최소화 (랜덤성 위험)
  2. 프롬프트 레벨에서 메타데이터 차단 필요
  3. 기존 최고 버전(34.04%) 유지
  4. 다음: Phase 3 (유형별 분석, 프롬프트 개선)
```

---

### Phase 3: 일반화 전략 (단기 목표)

**목적**: Public/Private 격차 원인 규명 + 취약 유형 식별 + 일반화 방향 수립

- [ ] 3.0 교차검증 및 일반화 분석

  - [ ] 3.1 **5-fold 교차검증** (analyze_cross_validation.py)
    - [ ] Train 254개를 5-fold로 분할 (sklearn.model_selection.KFold)
    - [ ] 각 fold별 Recall/Precision 측정:
      - [ ] Fold 1 (~51개): Recall, Precision 기록
      - [ ] Fold 2 (~51개): Recall, Precision 기록
      - [ ] Fold 3 (~51개): Recall, Precision 기록
      - [ ] Fold 4 (~50개): Recall, Precision 기록
      - [ ] Fold 5 (~51개): Recall, Precision 기록
    - [ ] 통계 분석:
      - [ ] Mean Recall ± Std 계산
      - [ ] 95% CI (Confidence Interval) 계산
      - [ ] Private LB 13.45%가 범위 내인지 확인
    - [ ] 판단:
      - [ ] 범위 밖 → "데이터 분포 차이" 확정
      - [ ] 범위 내 → "정상 변동" 또는 "과적합 의심"
    - [ ] 산출물: `outputs/logs/experiments/phase3_cross_validation.json`
      ```json
      {
        "experiment_date": "2025-10-23",
        "n_folds": 5,
        "folds": [...],
        "mean_recall": 33.5,
        "std_recall": 1.2,
        "cv_95_ci": [31.1, 35.9],
        "private_lb_in_range": false
      }
      ```

  - [ ] 3.2 **유형별 성과 분석** (analyze_error_type_performance.py)
    - [ ] 각 오류 유형별 Recall/Precision 계산 (20개 유형)
    - [ ] 평균 ± 표준편차 기준 취약 유형 식별:
      - [ ] 취약 유형: Recall < (평균 - 1σ)
      - [ ] 강점 유형: Recall > (평균 + 1σ)
    - [ ] 유형별 Train 샘플 수 vs 성과 상관 분석
    - [ ] Private 취약 가능 유형 추정 (낮은 Recall + 높은 분산)
    - [ ] 산출물: `outputs/analysis/error_type_performance.csv`

  - [ ] 3.3 **Public/Private 격차 원인 분석**
    - [ ] 교차검증 결과 + 유형별 분석 종합
    - [ ] 가설 검증:
      - [ ] 가설 1: 데이터 분포 차이 (교차검증 범위 밖)
      - [ ] 가설 2: 특정 유형 과적합 (유형별 편차 큼)
      - [ ] 가설 3: 채점 방식 차이 (주최측 문의 필요)
    - [ ] 일반화 전략 수립:
      - [ ] 취약 유형 보강 방안
      - [ ] 유형별 균형 개선 방안
      - [ ] Few-shot 재설계 방향
    - [ ] 산출물: `outputs/logs/experiments/phase3_generalization_analysis.md`

  - [ ] 3.4 **Phase 3 완료 검증**
    - [ ] 문서 업데이트
    - [ ] GitHub 동기화
    - [ ] Phase 3 결과 로그: `outputs/logs/experiments/phase3_generalization.json`

**Phase 3 성공 기준:**
```yaml
필수:
  - 5-fold 교차검증 완료 (분산 측정)
  - Private 13.45%가 95% CI 범위 밖 확인
  - 취약 오류 유형 식별 (3개 이상)
  - 일반화 전략 수립

분석 목표:
  - CV Mean Recall: 33-35%
  - CV Std: < 2%p
  - 유형별 Recall 편차: < 10%p (균형 개선 필요성 확인)

산출물:
  - phase3_cross_validation.json (교차검증 결과)
  - error_type_performance.csv (유형별 분석)
  - phase3_generalization_analysis.md (종합 분석)
  - phase3_generalization.json (Phase 결과)
```

---

### Phase 4: 프롬프트 최적화 (중기 목표)

**목적**: 메타데이터 억제 + 유형별 균형 + 형식 안정화

- [ ] 4.0 프롬프트 형식 및 구조 개선

  - [ ] 4.1 **형식 제약 A/B 실험** (prompt_ab_test.py)
    - [ ] 샘플 선정: train.csv에서 20개 (stratified sampling)
    - [ ] Version A (기존):
      ```
      System: "당신은 한국어 문법 교정 전문가입니다."
      User: "{err_sentence}"
      ```
    - [ ] Version B (형식 제약 강화):
      ```
      System: "당신은 한국어 문법 교정 전문가입니다.

      출력 규칙:
      1. 교정된 문장만 출력 (설명 금지)
      2. 콜론(:), 줄바꿈 절대 금지
      3. "원문:", "교정:" 라벨 금지

      출력: [교정된 문장]"
      User: "{err_sentence}"
      ```
    - [ ] 측정 항목:
      - [ ] 메타데이터 출현 빈도: n/20 케이스
      - [ ] 평균 토큰 수: Version A vs B
      - [ ] 파싱 오류: 형식 위반 횟수
      - [ ] 재시도 필요: 재생성 횟수
      - [ ] Recall/Precision: 성능 영향
    - [ ] 판단 기준:
      - [ ] 메타데이터 50% 감소 + Recall 유지 → Version B 채택
      - [ ] Recall 하락 > 1%p → Version A 유지
    - [ ] 산출물: `outputs/analysis/prompt_format_ab_test.json`

  - [ ] 4.2 **Few-shot 재설계 (유형별 균형)** (prompts/fewshot_balanced.py)
    - [ ] Phase 3.2 결과 활용 (취약 유형 우선 보강)
    - [ ] 커버리지 목표: 80% 이상
      - [ ] 현재 Few-shot v2: 52% (상위 3개 유형만)
      - [ ] 개선: 상위 10개 유형 × 1개 = 10개 예시
    - [ ] 토큰 제한 고려:
      - [ ] 예시당 평균 토큰: ~100
      - [ ] 10개 예시 = ~1000 토큰
      - [ ] System + User 메시지: ~500 토큰
      - [ ] 총 ~1500 토큰 (2000 제한 내)
    - [ ] 예시 없는 유형: < 20% (목표)
    - [ ] 산출물: `code/src/prompts/fewshot_balanced.py`

  - [ ] 4.3 **Multi-turn 소규모 탐색** (선택적)
    - [ ] 조건: Phase 4.1 완료 + 형식 제약 안정화
    - [ ] 샘플: 30개
    - [ ] 구조:
      - [ ] Turn 1: 오류 탐지 (JSON 배열)
      - [ ] Turn 2: 교정 실행
      - [ ] (Turn 3: 검증 - 선택적)
    - [ ] 측정:
      - [ ] Recall 개선: Single-turn vs Multi-turn
      - [ ] 토큰 사용량: 평균 토큰 × 2-3배
      - [ ] API 호출: 2-3회 (제한 준수 확인)
    - [ ] 판단:
      - [ ] Recall +2%p 이상 + 토큰 <2000 → 채택 검토
      - [ ] 그 외 → 보류
    - [ ] 산출물: `outputs/analysis/multiturn_exploration.json`

  - [ ] 4.4 **Phase 4 완료 검증**
    - [ ] 최적 프롬프트 버전 확정 (A/B 결과 기반)
    - [ ] 문서 업데이트
    - [ ] GitHub 동기화
    - [ ] Phase 4 결과 로그: `outputs/logs/experiments/phase4_prompt_optimization.json`

**Phase 4 성공 기준:**
```yaml
필수:
  - 형식 제약 A/B 실험 완료
  - Few-shot 재설계 완료 (커버리지 80%+)
  - 최적 프롬프트 버전 확정

성능 목표:
  - 메타데이터 출현: 50% 감소 (20개 → 10개 이하)
  - Recall 유지 또는 개선: ±1%p 범위
  - 커버리지: 80%+ (예시 없는 유형 <20%)

산출물:
  - prompt_format_ab_test.json (A/B 실험 결과)
  - fewshot_balanced.py (개선 프롬프트)
  - multiturn_exploration.json (선택적)
  - phase4_prompt_optimization.json (Phase 결과)
```

---

### Phase 5: 통합 개선 버전 (중기 완성) ✅

**목적**: 최적 규칙 + 최적 프롬프트 통합 + 최종 검증

- [x] 5.0 통합 개선 버전 실험

  - [x] 5.1 **최적 조합 구성** (2025-10-24 완료)
    - [x] Option A 확정: fewshot_v3 (검증됨) + EnhancedPostprocessor
    - [x] 버전 식별자:
      - [x] 파일명: `submission_fewshot_v3_enhanced_test.csv`
      - [x] 메타데이터:
        ```json
        {
          "version": "fewshot_v3_enhanced",
          "postprocessing": {
            "type": "EnhancedPostprocessor",
            "features": [
              "metadata_whitelist",
              "duplicate_sentence_removal",
              "decimal_point_exception",
              "number_unit_restoration"
            ]
          },
          "prompt": {
            "type": "fewshot_v3",
            "examples": 13
          },
          "date": "2025-10-24"
        }
        ```
    - [x] 산출물: generate_test_submission.py

  - [x] 5.2 **내부 리그 검증** (2025-10-24 완료)
    - [x] Train 254개 전체 재평가 완료
    - [x] Phase 3 회귀 테스트 (62개):
      - [x] Recall: 45.76% (기존과 동일) ✅
      - [x] 타깃 교정: 50.0% (기존과 동일) ✅
      - [x] 길이 폭발: 2개 (관리 가능) ✅
    - [x] Phase 5 재평가 (254개):
      - [x] Recall: 36.73% (목표 40% 대비 -3.27%p)
      - [x] 타깃 교정: 40.9%
      - [x] 메타데이터: 1.6% (목표 5% 이하) ✅
      - [x] 길이 폭발: 8개 (관리 가능) ✅
    - [x] 후처리 개선 효과:
      - [x] Recall: 35.92% → 36.73% (+0.81%p)
      - [x] 메타데이터: 2.4% → 1.6% (-0.8%p)
    - [x] 산출물: `outputs/experiments/phase5_full_train_results.csv`

  - [x] 5.3 **최종 LB 제출 파일 생성** (2025-10-24 완료)
    - [x] Test 110개 교정 실행 완료
    - [x] 제출 파일 형식 검증 완료
    - [x] 수동 수정 (숫자 분리 2개, 중복 문장 제거)
    - [x] 최종 검증 통과:
      - [x] 메타데이터: 0개 ✅
      - [x] 숫자 분리: 0개 ✅
      - [x] 중복 문장: 0개 ✅
    - [x] 산출물: `outputs/submissions/test/submission_fewshot_v3_enhanced_test.csv`

  - [ ] 5.4 **Phase 5 완료 검증** (LB 제출 대기)
    - [ ] LB 제출 실행
    - [ ] Public/Private LB 결과 분석
    - [ ] 격차 변화 확인 (20%p → ?%p)
    - [ ] 문서 업데이트 (EXPERIMENT_LOG_SUMMARY.md)
    - [ ] GitHub 동기화
    - [ ] Phase 5 결과 로그: `outputs/logs/phase6_test_submission_summary.md` (작성 완료)

**Phase 5 성공 기준:**
```yaml
필수:
  - 최적 조합 구성 완료 (규칙 + 프롬프트)
  - 내부 리그 검증 통과 (정상 범위 내)
  - LB 제출 완료

성능 목표 (중기):
  - Public LB: 35-36% (현재 34.04% → +1-2%p)
  - Private LB: 13.5-14.5% (현재 13.45% → +0.5-1%p)
  - 격차: 19-20%p (현재 20.6%p → 1%p 축소)

보정 플랜 (목표 미달 시):
  1. 프롬프트 형식 제약 강화 (Phase 4.1 재실행)
  2. Few-shot 예시 조정 (커버리지 재확인)
  3. 규칙 조합 재조정 (Phase 2.3.1 재검토)
  4. 유형별 가중치 조정
  5. 2회 반복 후 개선 없으면 현상 수용

산출물:
  - internal_league_validation.json (내부 검증)
  - submission_integrated_v5.3_test.csv (LB 제출)
  - phase5_integrated_version.json (Phase 결과)
```

---

### Phase 6: 고급 프롬프트 기법 (조건부)

**진행 조건:**
```yaml
필수:
  - Phase 2~5 모두 완료 (모든 Task ✅)

권장 (다음 중 하나 이상 만족):
  - Public/Private 격차 < 18%p (현재 20.6%p → 2.6%p 축소)
  - 또는: 교차검증 안정적 (CV Std < 2%p)
  - 또는: 팀 판단 (일반화 문제 해결 확인)

판단 기준:
  "기본 파이프라인이 안정화되었고,
   고급 기법이 도움이 될 것으로 판단되면 진행"
```

**제한 범위 (격차별):**
```yaml
격차 20%p 이상:
  - Rule-Checklist: ✅ 적용 (Phase 2 완료)
  - CD-CoT 이상: ❌ 보류

격차 18-20%p:
  - Rule-Checklist: ✅ 적용
  - CD-CoT: ⚠️ 소규모 실험 (20개 샘플)
  - ToT 이상: ❌ 보류

격차 18%p 이하:
  - 모든 고급 기법: ✅ 진행 가능
```

- [ ] 6.0 고급 프롬프트 기법 실험 (조건부)

  - [ ] 6.1 **Rule-Checklist 후처리** (Phase 2에서 완료)
    - [완료] 콜론 로직 개선
    - [완료] 규칙별 순효과 분석
    - [완료] 60% 길이 가드

  - [ ] 6.2 **Contrastive Denoising (CD-CoT)** (prompts/cd_cot.py)
    - [ ] 조건: 격차 < 18%p 또는 소규모 실험 승인
    - [ ] 잘못된 교정 예시와 올바른 교정 대비 프롬프트
    - [ ] 노이즈 제거 메커니즘 구현
    - [ ] 일관성 투표 시스템 구현
    - [ ] 예상 효과: +10-15%p (2024년 +17.8% 검증)
    - [ ] 산출물: cd_cot.py, 실험 결과 JSON

  - [ ] 6.3 **3-Expert Tree-of-Thought** (prompts/three_experts_tot.py)
    - [ ] 조건: 격차 < 18%p
    - [ ] Expert A (Detector) - 오류 탐지 전문가
    - [ ] Expert B (Corrector) - 교정 전문가
    - [ ] Expert C (Referee) - 검증 및 규칙 적용
    - [ ] JSON 기반 Expert 간 통신 프로토콜
    - [ ] 통합 파이프라인 구축
    - [ ] 예상 효과: +5-7%p
    - [ ] 산출물: three_experts_tot.py

  - [ ] 6.4 **Self-Consistency 앙상블** (utils/self_consistency.py)
    - [ ] 조건: 격차 < 18%p
    - [ ] 3개 샘플 생성 (temperature 0.1-0.3)
    - [ ] 다수결/일치도 기반 선택
    - [ ] Expert C에만 적용 (API 제한 최적화)
    - [ ] 예상 효과: +3-4%p
    - [ ] 산출물: self_consistency.py

  - [ ] 6.5 **Instance-Adaptive Prompting** (prompts/instance_adaptive.py)
    - [ ] 조건: 격차 < 18%p
    - [ ] 오류 유형별 특화 프롬프트 자동 선택
    - [ ] 동적 프롬프트 조정 메커니즘
    - [ ] 예상 효과: +2-3%p

  - [ ] 6.6 **Logic-of-Thought (LoT)** (prompts/logic_of_thought.py)
    - [ ] 조건: 격차 < 18%p
    - [ ] 문법 규칙을 논리식으로 표현
    - [ ] 명제 논리 기반 추론 체인
    - [ ] 예상 효과: CoT 대비 +4.35%

  - [ ] 6.7 **TEXTGRAD** (utils/textgrad.py)
    - [ ] 조건: 격차 < 18%p
    - [ ] 자연어 피드백을 gradient로 활용
    - [ ] 반복적 개선 메커니즘

  - [ ] 6.8 **각 기법별 성능 측정 및 비교**
  - [ ] 6.9 **최적 전략 조합 선택**
  - [ ] 6.10 **Phase 6 완료 검증**
    - [ ] 문서 업데이트
    - [ ] GitHub 동기화
    - [ ] Phase 6 결과 로그: `outputs/logs/experiments/phase6_advanced_techniques.json`

**Phase 6 성공 기준 (조건부):**
```yaml
진행 여부:
  - Phase 2~5 완료 필수
  - 격차 18%p 이하 권장

성능 목표 (장기, 이상적):
  - Public LB: 36-38%
  - Private LB: 15-17%
  - 격차: 15-18%p 이하

산출물:
  - 각 기법별 프롬프트 모듈
  - phase6_advanced_techniques.json (Phase 결과)
```

---

### Phase 7: 실험 자동화 시스템 (기존 3.0)

- [ ] 7.0 실험 자동화 시스템 구축
  - [ ] 7.1 프롬프트 버전 관리 시스템 (prompt_manager.py)
  - [ ] 7.2 배치 실험 실행기 (batch_runner.py)
  - [ ] 7.3 실험 로그 저장 시스템 (JSON 형식)
  - [ ] 7.4 체크포인트 및 재시작 기능
  - [ ] 7.5 토큰 제한 모니터링 시스템
  - [ ] 7.6 API 호출 제한 관리 시스템
  - [ ] 7.7 Phase 5 결과 검증 로그를 입력 조건으로 연결
  - [ ] 7.8 **Phase 7 완료 검증**
    - [ ] 문서 업데이트
    - [ ] GitHub 동기화

---

### Phase 8: 최적화 및 분석 시스템 (기존 4.0)

- [ ] 8.0 최적화 및 분석 시스템 개발
  - [ ] 8.1 실험 결과 분석기 (result_analyzer.py)
  - [ ] 8.2 오류 유형별 성능 매트릭스 생성
  - [ ] 8.3 최적 템플릿 자동 선택기 (optimizer.py)
  - [ ] 8.4 오류 패턴별 프롬프트 추천 시스템
  - [ ] 8.5 앙상블 전략 실험 (선택적)
  - [ ] 8.6 Public/Private 과적합 방지 전략 수립
  - [ ] 8.7 **Phase 8 완료 검증**
    - [ ] 문서 업데이트
    - [ ] GitHub 동기화

---

### Phase 9: 최종 제출 준비 (기존 5.0)

- [ ] 9.0 최종 제출 준비
  - [ ] 9.1 최종 프롬프트 템플릿 확정
  - [ ] 9.2 Test 데이터 처리 (test.csv → submission.csv)
  - [ ] 9.3 제출 파일 형식 검증
  - [ ] 9.4 최종 성능 문서화
  - [ ] 9.5 실험 과정 및 인사이트 정리
  - [ ] 9.6 GitHub 최종 백업 및 동기화

---

## 실험 우선순위 (전문가 조언 반영)

### Phase 1: 베이스라인 측정 (완료 ✅)
- ✅ 베이스라인 성능 측정 (Train 32.24%, Public 34.04%, Private 13.45%)
- ✅ 데이터셋 분석 완료 (20개 오류 유형)
- ✅ Few-shot 과적합 확인 (Train 35.92% → LB 31.91%)
- ✅ 콜론 버그 발견 (83% 텍스트 손실)

### Phase 2: 기본 안정화 (오늘 즉시 ⚡)
**우선순위**: 최우선
**예상 시간**: 2-3시간
**목표**: 규칙 검증 + 길이 가드 + 안정된 베이스라인

1. **규칙별 순효과 분석** (1-2시간)
   - 구현 난이도: ⭐⭐ (중간)
   - version_comparison.csv 41건 분석
   - 유지/제거 근거 확보

2. **60% 길이 가드 구현** (30분-1시간)
   - 구현 난이도: ⭐ (낮음)
   - Dry-run으로 영향도 확인
   - 83% 손실 재발 방지

3. **개선 버전 LB 제출**
   - Public 34.5%+, Private 14.0%+ 목표

### Phase 3: 일반화 전략 (내일 ⚡)
**우선순위**: 최우선
**예상 시간**: 3-4시간
**목표**: 격차 원인 규명 + 취약 유형 식별

1. **5-fold 교차검증** (2-3시간)
   - 구현 난이도: ⭐⭐ (중간)
   - 성능 분산 측정
   - Private 격차 원인 규명

2. **유형별 성과 분석** (1-2시간)
   - 구현 난이도: ⭐⭐ (중간)
   - 취약 유형 식별
   - 일반화 방향 수립

### Phase 4: 프롬프트 최적화 (모레)
**우선순위**: 중요
**예상 시간**: 2-3시간
**목표**: 메타데이터 억제 + 유형별 균형

1. **형식 제약 A/B** (1-2시간)
   - 구현 난이도: ⭐⭐ (중간)
   - 메타데이터 50% 감소 목표

2. **Few-shot 재설계** (1-2시간)
   - 구현 난이도: ⭐⭐ (중간)
   - 커버리지 80%+ 목표

3. **Multi-turn 탐색** (선택적)
   - 구현 난이도: ⭐⭐⭐ (높음)
   - 효과 검증 후 판단

### Phase 5: 통합 개선 버전 (3일차)
**우선순위**: 중요
**예상 시간**: 2-3시간
**목표**: 최적 조합 + 최종 검증

1. **내부 리그 검증** (1시간)
2. **최종 LB 제출** (1시간)
3. **결과 분석 및 문서화** (1시간)

### Phase 6: 고급 기법 (조건부)
**우선순위**: 조건부
**조건**: Phase 2~5 완료 + 격차 < 18%p
**예상 시간**: 4-8시간

1. **CD-CoT** (2-3시간) - 최고 ROI
2. **3-Expert ToT** (2-3시간)
3. **Self-Consistency** (1-2시간)
4. 기타 기법 (선택적)

### Phase 7-9: 자동화 및 최종화
**우선순위**: 낮음
**조건**: 핵심 성능 확보 후

---

## 성공 기준 (전문가 조언 반영)

### 단기 목표 (오늘~내일, Phase 2-3 완료)
```yaml
필수 달성:
  - [x] Phase 2 완료:
    - 규칙 순효과 분석 완료 (유지/제거 근거 확보)
    - 60% 길이 가드 구현 및 테스트 통과
    - Dry-run 롤백 비율 < 5%

  - [x] Phase 3 완료:
    - 5-fold 교차검증 완료 (분산 측정)
    - Private 13.45%가 95% CI 범위 밖 확인
    - 취약 오류 유형 식별 (3개 이상)
    - 일반화 전략 수립

성능 목표:
  - Public LB: 34.5%+ (현재 34.04% → +0.5%p 최소)
  - Private LB: 14.0%+ (현재 13.45% → +0.5%p 최소)
  - 또는: 콜론 버그 8건 해결 확인

분석 목표:
  - CV Mean Recall: 33-35%
  - CV Std: < 2%p
  - 유형별 Recall 편차 파악
```

### 중기 목표 (2-3일, Phase 4-5 완료)
```yaml
필수 달성:
  - [x] Phase 4 완료:
    - 형식 제약 A/B 실험 완료
    - Few-shot 재설계 완료 (커버리지 80%+)
    - 최적 프롬프트 버전 확정

  - [x] Phase 5 완료:
    - 최적 조합 구성 (규칙 + 프롬프트)
    - 내부 리그 검증 통과
    - LB 제출 완료

성능 목표:
  - Public LB: 35-36% (현재 34.04% → +1-2%p)
  - Private LB: 13.5-14.5% (현재 13.45% → +0.5-1%p)
  - 격차: 19-20%p (현재 20.6%p → 1%p 축소)

일관성 목표:
  - CV와 Full Train 차이 < 2%p
  - 메타데이터 출현 50% 감소
  - 커버리지 80%+

보정 플랜 (목표 미달 시):
  1. 프롬프트 형식 제약 강화 (Phase 4.1 재실행)
  2. Few-shot 예시 조정 (커버리지 재확인)
  3. 규칙 조합 재조정 (Phase 2.3.1 재검토)
  4. 유형별 가중치 조정
  5. 2회 반복 후 개선 없으면 현상 수용
```

### 장기 목표 (이상적, 대회 종료 전)
```yaml
선택 달성 (조건부):
  - [x] Phase 6 완료 (조건: 격차 < 18%p):
    - CD-CoT 또는 ToT 구현
    - 고급 기법 효과 검증

  - [x] Phase 7-9 완료:
    - 실험 자동화 시스템
    - 최종 제출 준비

성능 목표 (이상적):
  - Public LB: 36-38%
  - Private LB: 15-17%
  - 격차: 15-18%p 이하

통합 목표:
  - 최적 규칙 + 최적 프롬프트 + 고급 기법 (조건부)
  - 재현 가능한 실험 프레임워크
  - 오류 유형별 최적 전략 도출
```

---

## 예상 성능 향상 로드맵 (전문가 조언 반영)

### 현실적 로드맵 (일반화 우선)

| 전략 | 현재 | 예상 개선 | 목표 Public | 목표 Private | 격차 |
|------|------|----------|------------|-------------|------|
| **Baseline** | 34.04% | - | 34.04% | 13.45% | 20.59%p |
| **+ Phase 2 (안정화)** | 34.04% | +0.5-1%p | 34.5-35% | 14.0-14.5% | ~20%p |
| **+ Phase 3 (일반화)** | 34.5-35% | 분석 | - | - | 원인 규명 |
| **+ Phase 4 (최적화)** | 34.5-35% | +0.5-1%p | 35-36% | 13.5-14.5% | 19-21%p |
| **+ Phase 5 (통합)** | 35-36% | 통합 | **35-36%** | **13.5-14.5%** | **19-20%p** |
| **+ Phase 6 (고급, 조건부)** | 35-36% | +1-2%p | 36-38% | 15-17% | 15-18%p |

### 이상적 로드맵 (고급 기법 포함, 조건부)

| 전략 | 예상 개선 | 목표 Recall | 검증 근거 |
|------|----------|------------|-----------|
| Baseline | - | 34.04% | LB 실측 |
| + Rule-Checklist (안정화) | +0.5-1%p | 34.5-35% | 콜론 버그 8건 해결 |
| + 일반화 전략 | 분석 | - | 격차 원인 규명 |
| + 프롬프트 최적화 | +0.5-1%p | 35-36% | 메타데이터 감소 + 균형 |
| + CD-CoT (조건부) | +2-3%p | 37-39% | 2024년 +17.8% (과도한 기대치 조정) |
| + 3-Expert ToT (조건부) | +1-2%p | 38-41% | ToT 효과 (보수적) |
| + Self-Consistency (조건부) | +1-2%p | 39-43% | 다수결 안정성 |

**주의**: 고급 기법 효과는 **일반화 문제 해결 후** 평가 가능. 현재는 Phase 2~5 완료가 최우선.

---

## 구현 가이드라인

### API 제한 준수 전략
```python
# 케이스당 최대 3회 호출
# Option 1: Sequential (안전)
expert_a_result = call_api(expert_a_prompt)  # 1회
expert_b_result = call_api(expert_b_prompt)  # 2회
expert_c_result = call_api(expert_c_prompt)  # 3회

# Option 2: Merged (효율적)
all_experts_prompt = combine_experts(a, b, c)
result = call_api(all_experts_prompt)  # 1회
self_refine_1 = call_api(critic_prompt)  # 2회
self_refine_2 = call_api(critic_prompt)  # 3회
```

### 토큰 제한 준수 (2000 토큰)
- Expert 프롬프트: 각 500 토큰 이내
- JSON 출력 형식으로 효율화
- 불필요한 설명 제거
- Few-shot 예시: 10개 × 100토큰 = 1000토큰

### 과적합 방지 원칙
1. Train 특화 규칙 지양
2. 일반 문법 원칙 중심
3. 모든 오류 유형 균등 처리
4. Test 데이터 절대 참조 금지
5. 교차검증으로 일반화 확인

### 로그 구조화
```
outputs/logs/experiments/
├── phase2_basic_stabilization.json
├── phase3_cross_validation.json
├── phase3_generalization.json
├── phase4_prompt_optimization.json
├── phase5_integrated_version.json
└── phase6_advanced_techniques.json (조건부)
```

### 문서 업데이트 (Mandatory)
- 각 Phase 완료 시 EXPERIMENT_LOG_SUMMARY.md 업데이트
- .gitignore 검증
- GitHub 동기화

---

## 중요 참고 문서

### 전략 문서
- `/docs/advanced/EXPERT_ADVICE_STRATEGY.md` - **전문가 조언 기반 전략** (최신)
- `/docs/advanced/ADVANCED_STRATEGIES.md` - 2024-2025 최신 기법
- `/docs/advanced/EXPERIMENT_LESSONS.md` - 과적합 분석 및 교훈

### 실험 로그
- `/outputs/logs/EXPERIMENT_LOG_SUMMARY.md` - 전체 실험 이력
- `/outputs/version_comparison.csv` - 버전 비교 (41건 차이)
- `/code/analyze_colon_patterns.py` - 콜론 버그 분석
- `/code/analyze_grammar_rules_effect.py` - 문법 규칙 효과 분석

### 워크플로우
- 항상 이 tasks 파일의 순서대로 진행
- Phase 단위로 완료 후 다음 Phase 진행
- 조건부 Phase는 조건 확인 후 진행

---

**최종 업데이트**: 2025-10-23 (전문가 조언 2차 반영)
**다음 리뷰**: Phase 2 완료 후 (규칙 검증 + 길이 가드 + LB 제출)
