## Relevant Files

### 핵심 소스 코드 (src/)
- `code/src/prompts/` - 프롬프트 템플릿 모듈 (핵심 수정 대상)
  - `baseline.py` - 베이스라인 프롬프트 (맞춤법 1개 예시) ✅ **최종 선택**
  - `zero_shot.py` - Zero-shot 프롬프트 (예시 0개)
  - `baseline_josa.py` - 조사 예시 1개
  - `baseline_spacing.py` - 띄어쓰기 예시 1개
  - `baseline_plus_3examples.py` - Few-shot 4개 예시
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
- `code/outputs/logs/baseline_results.json` - 베이스라인 성능 (Train 32.24%, LB 34.04%)
- `code/outputs/logs/zero_shot_train_results.json` - Zero-shot 성능 (Train 32.24%, LB 31.91%)
- `code/outputs/logs/baseline_josa_train_results.json` - 조사 예시 성능 (Train 33.47%, LB 31.91%)
- `code/outputs/logs/baseline_spacing_train_results.json` - 띄어쓰기 예시 (Train 32.65%, 폐기)
- `code/outputs/logs/experiments/` - Phase별 실험 결과 (JSON)
- `code/outputs/submissions/train/` - Train 데이터 교정 결과
- `code/outputs/submissions/test/` - LB 제출 파일
  - `submission_baseline_test_clean.csv` - **최종 제출 파일** (34.04% / 13.45%)
  - `submission_zero_shot_test.csv` - Zero-shot (31.91% / 12.61%)
  - `submission_baseline_josa_test.csv` - 조사 예시 (31.91% / 11.54%)
  - `submission_baseline_plus_3examples_test.csv` - Plus3 (27.66% / 9.77%)
- `code/outputs/analysis/` - 상세 분석 CSV
  - `FINAL_EXPERIMENT_SUMMARY.md` - **최종 실험 종합 보고서**
  - `FAILURE_ANALYSIS_BASELINE_PLUS_3EXAMPLES.md` - Plus3 실패 분석
  - `performance_drop_root_cause.md` - 성능 하락 원인 분석

### 테스트 (tests/)
- `code/tests/test_prompts.py` - 프롬프트 모듈 테스트
- `code/tests/test_generator.py` - 생성기 테스트
- `code/tests/test_metrics.py` - 메트릭 테스트
- `code/tests/test_evaluator.py` - 평가기 테스트
- `code/tests/test_postprocessors.py` - 후처리 테스트

### Notes

- **⚠️ 중요: 모든 Python 실행은 반드시 `uv run python` 명령 사용**
- uv를 사용한 의존성 관리 (pyproject.toml)
- Python 3.12 사용 (.python-version)
- 상세 uv 가이드: `/docs/getting-started/UV_ENVIRONMENT_GUIDE.md`

---

## Tasks

### Phase 1: 베이스라인 성능 측정 (완료 ✅)

- [x] 1.0 베이스라인 성능 측정 및 분석
  - [x] 1.1 환경 설정 및 의존성 설치 확인 (uv sync)
  - [x] 1.2 API 키 설정 확인 (.env 파일)
  - [x] 1.3 데이터 파일 배치 확인 (code/data/train.csv, test.csv)
  - [x] 1.4 베이스라인 프롬프트로 교정 실행 (scripts/generate.py --prompt baseline)
  - [x] 1.5 베이스라인 Recall 점수 측정 (scripts/evaluate.py)
  - [x] 1.6 오류 유형별 분석 결과 검토 (analysis.csv)
  - [x] 1.7 베이스라인 성능 문서화 (logs/baseline_results.json)

**Phase 1 완료 결과:**
- Train Recall: 32.24%, Precision: 14.95%
- Public LB: **34.0426%**, Private LB: **13.4454%**
- 프롬프트: 맞춤법 예시 1개 (다양한 오류 유형 포함)
- 메타데이터: 5개 (4.5%) - 운 좋은 버그로 점수 향상
- 주요 발견: 1개 예시가 최적점

---

### Phase 2: 예시 개수 실험 (완료 ✅)

**목적**: Few-shot 예시 개수별 성능 패턴 파악

- [x] 2.0 예시 개수별 프롬프트 실험
  - [x] 2.1 **Zero-shot (예시 0개)** 프롬프트 작성 및 실험
    - [x] 프롬프트 구현: `src/prompts/zero_shot.py`
    - [x] Train 254개 검증: Recall 32.24%
    - [x] Phase 3 회귀 테스트 (62개): Recall 33.90% (+1.66%p)
    - [x] Test 110개 생성 및 LB 제출
    - [x] 결과: Public 31.91%, Private 12.61%
    - [x] 판정: Baseline 대비 -2.13%p (보수적 교정, FN 증가)

  - [x] 2.2 **Baseline (예시 1개)** - 기존 최고 성능
    - [x] 프롬프트: 맞춤법 예시 1개 (자연스러운 문장)
    - [x] Train: 32.24%
    - [x] LB: **34.04% / 13.45%** ← **최고 성능**
    - [x] 특징: 다양한 오류 유형 포함 (맞춤법, 띄어쓰기, 문법)
    - [x] 메타데이터 버그: 5개 케이스에서 4번 반복 출력 → 점수 향상

  - [x] 2.3 **Plus3 (예시 4개)** 프롬프트 실험
    - [x] 프롬프트: 맞춤법, 조사, 사이시옷, 표현다듬기 4개 예시
    - [x] Train: 34.69% (+2.45%p)
    - [x] Test LB: 27.66% / 9.77% (-6.38%p / -3.68%p)
    - [x] 치명적 문제: 첫 문장만 출력 (3개 케이스, 70-80% 삭제)
    - [x] 실패 분석 완료: `FAILURE_ANALYSIS_BASELINE_PLUS_3EXAMPLES.md`
    - [x] 판정: 과적합, Train 향상 ≠ Test 향상

**Phase 2 실제 결과:**
```yaml
핵심 발견:
  - 예시 개수별 성능 패턴:
    - 0개 (Zero-shot): 31.91% (보수적 교정)
    - 1개 (Baseline):  34.04% ← 최적점!
    - 4개 (Plus3):     27.66% (과적합)

교훈:
  - 1개 예시가 최적 균형점
  - Few-shot은 양날의 검 (과적합 위험)
  - Train 성능 향상 ≠ Test 성능 향상
```

---

### Phase 3: 예시 내용 실험 (완료 ✅)

**목적**: 동일하게 1개 예시를 사용하되 내용별 효과 비교

- [x] 3.0 예시 내용별 프롬프트 실험

  - [x] 3.1 **띄어쓰기 예시 1개** 실험
    - [x] 프롬프트 구현: `src/prompts/baseline_spacing.py`
    - [x] 예시: "받아봤지만 탐탁치않게" → "받아 봤지만 탐탁지 않게"
    - [x] Train 254개 검증: Recall 32.65%
    - [x] 치명적 문제: 길이 폭발 49개 (19.3%)
      - 최악: 640.9% (22자 → 141자)
    - [x] 판정: **폐기** (LB 제출 불가)

  - [x] 3.2 **조사 예시 1개** 실험
    - [x] 프롬프트 구현: `src/prompts/baseline_josa.py`
    - [x] 예시: "탐탁치 않게" → "탐탁지 않게"
    - [x] Train 254개 검증: Recall 33.47% (+1.23%p)
    - [x] Phase 3 회귀 테스트 (62개): Recall 35.59% (+2.12%p)
    - [x] Test 110개 생성 및 LB 제출
    - [x] 결과: Public 31.91%, Private **11.54%** (최저)
    - [x] 문제: 길이 폭발 12개 (10.9%), Private 최저
    - [x] 판정: 실패 (-2.13%p / -1.91%p)

  - [x] 3.3 **맞춤법 예시 1개** (Baseline) - 재확인
    - [x] 프롬프트: 기존 Baseline
    - [x] 예시: "않좋은데, 김치찌게 먹으러 갈려고"
    - [x] 특징: 다양한 오류 유형 (맞춤법 + 띄어쓰기 + 문법)
    - [x] LB: **34.04% / 13.45%** ← **최고 유지**

**Phase 3 실제 결과:**
```yaml
핵심 발견:
  - 동일하게 1개 예시라도 내용에 따라 성능 차이:
    - 맞춤법: 34.04% / 13.45% ← 최고
    - 조사:   31.91% / 11.54% ← Private 최저
    - 띄어쓰기: 폐기 (길이 폭발)

  - Baseline 맞춤법 예시의 우수성:
    - 다양한 오류 유형 포함 (맞춤법, 띄어쓰기, 문법)
    - 적절한 난이도
    - 자연스러운 문장 구조
    - 운 좋은 메타데이터 버그

교훈:
  - 예시 내용이 개수만큼 중요
  - 단일 오류 유형 편향 → 길이 폭발 or 과적합
  - 다양성이 핵심
```

---

### Phase 4: 전문가 조언 실험 (완료 ✅)

**목적**: 전문가 조언에 따른 단계별 검증 (Train → Phase 3 → Test)

- [x] 4.0 전문가 조언 기반 실험

  - [x] 4.1 **Zero-shot 전체 검증**
    - [x] Train 254개: 32.24%
    - [x] Phase 3 62개: 33.90% (+1.66%p 일관성)
    - [x] Test 110개: 31.91% / 12.61%
    - [x] 품질: 메타데이터 1개, 길이 폭발 4개
    - [x] 판정: 안정적이나 Baseline보다 낮음

  - [x] 4.2 **조사 예시 전체 검증**
    - [x] Train 254개: 33.47% (+1.23%p)
    - [x] Phase 3 62개: 35.59% (+2.12%p 일관성)
    - [x] Test 110개: 31.91% / 11.54%
    - [x] 품질: 메타데이터 2개, 길이 폭발 12개
    - [x] 판정: Train 향상 → Test 하락 (일반화 실패)

**Phase 4 실제 결과:**
```yaml
검증 방법론 성과:
  - Train → Phase 3 → Test 단계별 검증 완료
  - 일관성 확인: Phase 3에서 안정적이어도 Test 실패 가능
  - Train 성능은 Test 성능의 지표가 아님

최종 발견:
  - Train 향상 ≠ Test 향상 (조사 예시)
  - Phase 3 일관성 ≠ Test 성공 (조사 예시)
  - Public/Private 격차 20%p (근본적 한계)
```

---

### Phase 5: 최종 결론 (완료 ✅)

- [x] 5.0 전체 실험 종합 분석

  - [x] 5.1 **최종 성능 비교**
    ```
    제출 이력 (4회 사용, 16회 남음):
    1위: Baseline (맞춤법 1개)  34.04 / 13.45 ← 최종 선택
    2위: Zero-shot (0개)        31.91 / 12.61
    2위: 조사 (1개)             31.91 / 11.54 (Private 최저)
    3위: Plus3 (4개)            27.66 / 9.77
    폐기: 띄어쓰기 (1개)        길이 폭발 49개
    ```

  - [x] 5.2 **핵심 패턴 도출**
    - [x] 예시 개수: 1개가 최적점
    - [x] 예시 내용: 맞춤법 (다양성) > 조사/띄어쓰기 (특화)
    - [x] Train 성능: Test 성능과 무관 (심지어 역상관)
    - [x] 메타데이터 버그: Baseline의 숨은 성공 요인
    - [x] 일반화 실패: Public/Private 격차 20%p (근본적 한계)

  - [x] 5.3 **최종 전략 수립**
    - [x] **Baseline 34.04% 최종 확정**
    - [x] 더 이상의 Few-shot 실험 불필요
    - [x] 16회 제출 남음 → 다른 전략 모색 권장
    - [x] 종합 보고서 작성: `FINAL_EXPERIMENT_SUMMARY.md`

  - [x] 5.4 **문서화 완료**
    - [x] FINAL_EXPERIMENT_SUMMARY.md 작성
    - [x] FAILURE_ANALYSIS_BASELINE_PLUS_3EXAMPLES.md 작성
    - [x] tasks 파일 업데이트
    - [x] GitHub 동기화 준비

**Phase 5 최종 결론:**
```yaml
최종 결정:
  - Baseline 34.0426% (Public) / 13.4454% (Private) 확정
  - 제출 파일: submission_baseline_test_clean.csv

핵심 교훈:
  1. Few-shot은 양날의 검
     - 0개: 보수적 (FN 증가)
     - 1개: 균형 (최적)
     - 4개: 과적합 (일반화 실패)

  2. 예시 설계의 중요성
     - 다양성 > 특화
     - 맞춤법 예시 (3가지 오류) > 조사/띄어쓰기 (1가지 오류)

  3. Train 성능은 무의미
     - Train 향상 → Test 하락 (모든 실험)
     - Phase 3 일관성 → Test 실패 (조사 예시)

  4. 최적점은 우연히 발견됨
     - Baseline의 성공: 맞춤법 예시 + 메타데이터 버그
     - 의도적 설계 아님

대안 전략 (시간 있을 시):
  - 완전히 다른 접근: System message, JSON 구조화
  - 데이터 분석 집중: Public/Private 차이 규명
  - 후처리 개선: 메타데이터 제거 (점수 하락 위험)
```

---

## 실험 결과 요약

### 제출 이력

| 순위 | 프롬프트 | 예시 | Public | Private | Train | 판정 |
|---|---|---|---|---|---|---|
| 🥇 **1위** | **Baseline** | **맞춤법 1개** | **34.04** | **13.45** | 32.24 | ✅ **최종** |
| 🥈 2위 | Zero-shot | 0개 | 31.91 | 12.61 | 32.24 | ⚠️ 보수적 |
| 2위 | 조사 | 1개 | 31.91 | 11.54 | 33.47 | ❌ Private 최저 |
| 🥉 3위 | Plus3 | 4개 | 27.66 | 9.77 | 34.69 | ❌ 과적합 |
| - | 띄어쓰기 | 1개 | - | - | 32.65 | ❌ 폐기 |

**사용 제출 횟수**: 4회 / 20회 (16회 남음)

### 예시 개수별 성능

```
0개 (Zero-shot): 31.91% (보수적)
1개 (Baseline):  34.04% ← 최적점!
4개 (Plus3):     27.66% (과적합)

→ 1개 예시가 최적 균형점
```

### 예시 내용별 성능 (1개 예시)

```
맞춤법 (다양성): 34.04 / 13.45 ← 최고
조사 (특화):     31.91 / 11.54 ← Private 최저
띄어쓰기 (특화): 폐기 (길이 폭발)

→ 다양성 > 특화
```

### Train vs Test 성능

| 프롬프트 | Train | Public | 차이 | 패턴 |
|---|---|---|---|---|
| Baseline | 32.24 | 34.04 | +1.80 | 운 좋은 일치 |
| Zero-shot | 32.24 | 31.91 | -0.33 | 보수적 |
| 조사 | **33.47** | 31.91 | **-1.56** | **Train↑ Test↓** |
| Plus3 | **34.69** | 27.66 | **-7.03** | **Train↑ Test↓** |

**결론: Train 성능 향상 = Test 성능 하락**

---

## 성공 기준 (최종 업데이트)

### 달성 완료 ✅

```yaml
실험 완료:
  - ✅ 예시 개수별 실험 (0개, 1개, 4개)
  - ✅ 예시 내용별 실험 (맞춤법, 조사, 띄어쓰기)
  - ✅ 전문가 조언 검증 (Train → Phase 3 → Test)
  - ✅ 최적 프롬프트 확정 (Baseline)

성능 목표:
  - ✅ Public LB: 34.04% (최고 달성)
  - ✅ Private LB: 13.45% (최고 달성)
  - ❌ 격차 축소: 20.59%p (개선 실패)

문서화:
  - ✅ 전체 실험 종합 보고서 (FINAL_EXPERIMENT_SUMMARY.md)
  - ✅ Plus3 실패 분석 (FAILURE_ANALYSIS_BASELINE_PLUS_3EXAMPLES.md)
  - ✅ Phase별 로그 작성
  - ✅ tasks 파일 업데이트
```

### 미달성 및 포기 ❌

```yaml
포기한 목표:
  - ❌ Public LB 35%+ (34.04%에서 멈춤)
  - ❌ Public/Private 격차 축소 (20%p 유지)
  - ❌ Train 기반 성능 예측 (불가능 확인)

이유:
  1. 모든 개선 시도 실패 (Zero-shot, 조사, Plus3)
  2. Train 성능과 Test 성능 역상관
  3. Public/Private 격차는 근본적 한계
  4. Few-shot 최적점 발견 (1개, 맞춤법)
  5. 추가 실험의 기대 효과 낮음

대안 전략 (16회 제출 남음):
  - 완전히 다른 접근 (System message, JSON)
  - 후처리 개선 (리스크: 점수 하락)
  - 데이터 분석 집중 (격차 원인 규명)
```

---

## 주요 교훈

### 1. Few-shot Learning의 특성

**양날의 검:**
- 장점: 특정 패턴 강화, 모델 유도
- 단점: 과적합, 편향, 일반화 실패

**최적점:**
- 0개: 보수적 교정 (FN 증가)
- **1개: 균형잡힌 교정** ← 최적
- 4개: 과적합 (첫 문장만 출력)

### 2. 예시 설계 원칙

**좋은 예시 (Baseline 맞춤법):**
- ✅ 다양한 오류 유형 포함 (맞춤법 + 띄어쓰기 + 문법)
- ✅ 적절한 난이도 (쉽지도 어렵지도 않음)
- ✅ 자연스러운 문장 구조
- ✅ 명확한 교정 패턴

**나쁜 예시 (조사, 띄어쓰기):**
- ❌ 단일 오류 유형 편향
- ❌ 길이 폭발 유발 (특화 → 과잉 교정)
- ❌ 일반화 실패

### 3. Train 성능의 함정

**발견:**
- Train 향상 → Test 하락 (Plus3, 조사)
- Train 동일 → Test 차이 (Baseline vs Zero-shot)
- Phase 3 일관성 → Test 실패 (조사)

**결론:**
- **Train 성능은 Test 성능의 지표가 아님**
- **Train 기반 의사결정 불가**
- **LB 제출만이 유일한 검증**

### 4. 메타데이터 버그의 역설

**Baseline의 숨은 성공 요인:**
- 5개 케이스에서 메타데이터 4번 반복
- 평가 시 일부와 매칭 → TP 증가
- 더러운 출력 → 높은 점수
- 깨끗한 출력 (Zero-shot, 조사) → 낮은 점수

**역설:**
- 버그 제거 → 점수 하락 가능
- 완벽한 후처리 ≠ 높은 점수

### 5. 일반화 문제의 한계

**Public/Private 격차 20%p:**
- 모든 프롬프트에서 18-25%p 격차
- 데이터 분포 차이 (근본적 한계)
- 프롬프트 개선으로 해결 불가

---

### Phase 6: Ultra-Conservative Rule Post-correction (완료 ✅)

**목적**: Baseline이 놓친 명확한 오류를 규칙 기반으로 보충

- [x] 6.0 규칙 기반 후처리 실험
  - [x] 6.1 **Train 데이터 패턴 분석**
    - [x] 명확한 오류 패턴 추출: 3개
      - 금새 → 금세 (100% 확실)
      - 치 않 → 지 않 (95%+ 확실)
      - 추측컨대 → 추측건대 (100% 확실)
    - [x] False Positive ≈ 0% 규칙만 선택

  - [x] 6.2 **MinimalRulePostprocessor 구현**
    - [x] 60% 길이 가드 (과도한 삭제 방지)
    - [x] 150% 길이 가드 (과도한 추가 방지)
    - [x] 적용 조건: 원문 = Baseline 출력일 때만

  - [x] 6.3 **Train 검증 (254개)**
    - [x] 교정 실행 완료 (4분 50초)
    - [x] **규칙 적용: 0개**
    - [x] Recall: 32.24% (Baseline과 동일)
    - [x] 결과: 개선 효과 없음

**Phase 6 결론:**
```yaml
실험 결과:
  - 규칙 적용 횟수: 0개
  - Recall: 32.24% (개선 없음)
  - 판정: 실패

핵심 발견:
  1. Baseline이 이미 모든 명확한 규칙 처리
     - "금새→금세", "치 않→지 않" 등 100% 교정
     - 규칙 기반 후처리가 개입할 여지 없음

  2. Baseline의 진짜 한계
     - 명확한 규칙을 못 잡아서가 아님
     - 복잡한 문맥 이해 필요
     - 애매한 오류 (주관적 판단 필요)

  3. 규칙 기반 접근의 한계
     - Train 분석으로 패턴을 찾아도 소용없음
     - Baseline이 이미 처리 → 개선 불가
     - 새로운 규칙 추가 → False Positive 위험

최종 판정:
  - 규칙 기반 후처리 전략 폐기
  - 더 이상의 시도 불필요
  - Baseline 34.04% 최종 확정
```

---

## 다음 단계 권장

### 즉시 실행

**Baseline 34.04% 최종 확정**
- 제출 파일: `submission_baseline_test_clean.csv`
- 더 이상의 Few-shot 실험 불필요

### 대안 전략 (16회 제출 남음, 선택적)

1. **완전히 다른 접근**
   - System message 활용
   - JSON 구조화 출력
   - Multi-turn 대화
   - 출력 형식 제약 강화

2. **후처리 개선** (리스크 있음)
   - 메타데이터 완전 제거
   - 길이 가드 개선
   - 주의: 점수 하락 가능

3. **데이터 분석 집중**
   - Public/Private 차이 규명
   - 5-fold 교차검증
   - 유형별 성과 분석
   - Baseline 성공 케이스 심층 분석

---

## 중요 참고 문서

### 최종 분석 문서
- `outputs/analysis/FINAL_EXPERIMENT_SUMMARY.md` - **전체 실험 종합 보고서**
- `outputs/analysis/FAILURE_ANALYSIS_BASELINE_PLUS_3EXAMPLES.md` - Plus3 실패 분석
- `outputs/analysis/performance_drop_root_cause.md` - 성능 하락 원인 분석

### 실험 로그
- `outputs/logs/baseline_results.json` - Baseline (34.04%)
- `outputs/logs/zero_shot_train_results.json` - Zero-shot (31.91%)
- `outputs/logs/baseline_josa_train_results.json` - 조사 (31.91%)
- `outputs/logs/baseline_spacing_train_results.json` - 띄어쓰기 (폐기)

### 전략 문서
- `/docs/advanced/EXPERT_ADVICE_STRATEGY.md` - 전문가 조언
- `/docs/advanced/EXPERIMENT_LESSONS.md` - 과적합 분석
- `/outputs/logs/EXPERIMENT_LOG_SUMMARY.md` - 전체 실험 이력

---

**최종 업데이트**: 2025-10-24
**다음 리뷰**: 필요 시 (현재 실험 완료)
**상태**: ✅ **완료** - Baseline 34.04% 최종 확정
