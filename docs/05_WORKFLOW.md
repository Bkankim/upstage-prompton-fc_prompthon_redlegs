# 전체 실험 워크플로우

> Phase 1-6 실험 과정의 재현 가이드

이 문서는 프로젝트 전체 실험 과정(Phase 1-6)을 단계별로 재현할 수 있도록 안내합니다.

---

## 개요

**실험 목표**: 프롬프트 엔지니어링만으로 한국어 문법 교정 Recall 최대화

**실험 기간**: Phase 1 (베이스라인) → Phase 6 (규칙 기반 후처리)

**최종 결과**: Baseline (맞춤법 예시 1개) - Public 34.04% / Private 13.45%

---

## Phase 1: 베이스라인 성능 측정 (완료)

### 목적
- 초기 성능 확인
- 개선 방향 파악
- 평가 기준 수립

### 실행 단계

#### 1단계: 환경 설정
```bash
# uv 설치
curl -LsSf https://astral.sh/uv/install.sh | sh

# 프로젝트 디렉토리로 이동
cd code

# 의존성 설치
uv sync

# API 키 설정
echo "UPSTAGE_API_KEY=your_key_here" > .env
```

#### 2단계: 데이터 확인
```bash
# Train 데이터 확인 (254개)
head -5 data/train.csv

# Test 데이터 확인 (109개)
head -5 data/test.csv
```

#### 3단계: Baseline 실행
```bash
# Train 데이터로 교정 실행
uv run python scripts/run_experiment.py --prompt baseline
```

#### 4단계: 결과 확인
```bash
# 평가 메트릭 확인
cat outputs/logs/baseline_results.json

# 예상 출력:
# {
#   "prompt": "baseline",
#   "train_performance": {
#     "recall": 32.24,
#     "precision": 14.79
#   }
# }
```

#### 5단계: Test 제출 파일 생성
```bash
# LB 제출용 파일 자동 생성됨
ls outputs/submissions/test/submission_baseline_test.csv
```

### 결과
- **Train Recall**: 32.24%
- **Public LB**: 34.04%
- **Private LB**: 13.45%
- **평가**: 최고 성능 (최종 선택)

### 발견
- 1개 예시로도 충분한 성능
- 메타데이터 버그 발견 (5개 케이스에서 4번 반복 출력 → 의도치 않은 점수 향상)
- Public-Private 격차 약 20%p (구조적 문제 발견)

---

## Phase 2: 예시 개수 실험 (완료)

### 목적
- Few-shot 예시 개수별 성능 패턴 파악
- 최적 예시 개수 도출

### 실험 2-1: Zero-shot (예시 0개)

#### 실행
```bash
# Zero-shot 프롬프트로 실행
uv run python scripts/run_experiment.py --prompt zero_shot
```

#### 결과
- **Train**: 32.24% (Baseline과 동일)
- **Public**: 31.91% (-2.13%p)
- **Private**: 12.61% (-0.84%p)

#### 분석
- 너무 보수적: 확실하지 않으면 원문 유지
- False Negative 증가
- 교훈: 최소 1개 예시는 필요

### 실험 2-2: Plus3 (예시 4개)

#### 실행
```bash
# 4개 예시 프롬프트로 실행
uv run python scripts/run_experiment.py --prompt baseline_plus_3examples
```

#### 결과
- **Train**: 34.69% (+2.45%p, 가장 높음!)
- **Public**: 27.66% (-6.38%p, 참패)
- **Private**: 9.77% (-3.68%p)

#### 충격적 발견
**긴 문장의 첫 문장만 출력하고 멈춤** (3개 케이스에서 70-80% 텍스트 삭제)

**원인**:
- Few-shot 예시가 모두 짧은 단일 문장
- 모델이 "이 정도 길이면 됐구나" 학습
- 길이 패턴 과적합

**교훈**:
- 더 많은 예시 != 더 좋은 성능
- Train 성능 향상 → Test 성능 하락 (과적합)

### Phase 2 결론

```
예시 개수 vs 성능:
0개 (Zero-shot): 31.91% - 보수적
1개 (Baseline):  34.04% - 최적점 [중요]
4개 (Plus3):     27.66% - 과적합

→ 1개 예시가 최적 균형점
```

---

## Phase 3: 예시 내용 실험 (완료)

### 목적
- 예시 내용 (오류 유형)에 따른 성능 차이 확인
- 특화 vs 다양성 비교

### 실험 3-1: 조사 특화 예시

#### 실행
```bash
# 조사 예시로 실행
uv run python scripts/run_experiment.py --prompt baseline_josa
```

#### 결과
- **Train**: 33.47% (+1.23%p 향상!)
- **Public**: 31.91% (-2.13%p)
- **Private**: 11.54% (-1.91%p, 최저)

#### 분석
- Train에서 좋아도 Test 실패
- 조사 오류에만 특화 → 다른 오류 소홀
- 일반화 실패

#### 교훈
**Train 성능은 Test의 지표가 아니다**

### 실험 3-2: 띄어쓰기 예시 (폐기)

#### 실행
```bash
# Train 검증만 실행 (LB 제출 안 함)
# 길이 폭발 49개 (19.3%) 발견 → 즉시 폐기
```

#### 결과
- **Train**: 32.65%
- **문제**: 길이 폭발 49개
- **판정**: LB 제출 안 함

### Phase 3 결론

**예시 다양성 > 특화**
- 맞춤법 예시 (3가지 오류 유형 포함) > 조사 예시 (1가지만)
- 단일 예시의 복잡도가 중요

---

## Phase 4-5: 종합 분석 및 전략 수립 (완료)

### 패턴 도출

#### 발견 1: Few-shot의 양날의 검
```
0개: 보수적 → FN 증가
1개: 균형 → 최적점
4개: 과적합 → 일반화 실패
```

#### 발견 2: Train 성능 무의미
| 프롬프트 | Train | Public | Train-Public 격차 |
|---------|-------|--------|------------------|
| Baseline | 32.24 | 34.04 | +1.80 (일반화 우수) |
| 조사 | 33.47 | 31.91 | -1.56 (과적합) |
| Plus3 | 34.69 | 27.66 | -7.03 (파국적 과적합) |

**패턴**: Train 성능 향상 → Test 성능 하락

#### 발견 3: Public/Private 격차 20%p
- 모든 실험에서 일관되게 발생
- 데이터 분포 차이 (구조적 문제)
- 프롬프트로 해결 불가

### 최종 전략

**Baseline 34.04% 최종 확정**

**근거**:
1. 모든 변형이 Baseline보다 나쁨
2. Train 성능은 Test와 무관
3. 16회 제출 남음

---

## Phase 6: 규칙 기반 후처리 (완료)

### 목적
- Baseline이 놓친 명확한 오류를 규칙으로 보충

### 전략

**Ultra-Conservative Rule Post-correction**
- 원문 = Baseline 출력일 때만 규칙 적용
- False Positive ≈ 0%인 규칙만 사용

### 구현

#### 1단계: 규칙 추출
```bash
# Train 데이터에서 명확한 패턴 추출
# (이미 실행 완료, 문서로만 확인 가능)
```

**추출된 규칙 3개**:
1. `금새` → `금세` (100% 확실)
2. `치 않` → `지 않` (형용사 뒤, 95%+ 확실)
3. `추측컨대` → `추측건대` (100% 확실)

#### 2단계: MinimalRulePostprocessor 구현
- 코드: `code/src/postprocessors/minimal_rule.py`
- 안전장치: 60-150% 길이 가드

#### 3단계: Train 검증
```bash
# Phase 6 규칙 검증
uv run python validate_baseline_minimal_rules.py
```

### 결과
```
규칙 적용: 0개
Recall: 32.24% (변화 없음)
```

### 원인 분석

**Baseline이 이미 모든 명확한 규칙을 100% 처리했음**

**핵심 깨달음**:
- Baseline 34%의 한계는 "명확한 규칙을 못 잡아서"가 아님
- 진짜 한계: 복잡한 문맥 이해, 애매한 오류 판단
- 규칙 기반 접근으로는 개선 불가능

### Phase 6 결론

**더 이상의 Few-shot/규칙 실험 불필요**

**최종 확정**: Baseline 34.04% 유지

---

## 전체 실험 요약

| Phase | 프롬프트 | 예시 | Train | Public | Private | 결과 |
|-------|---------|------|-------|--------|---------|------|
| 1 | Baseline | 1개 | 32.24 | **34.04** | **13.45** | [완료] 최고 |
| 2 | Zero-shot | 0개 | 32.24 | 31.91 | 12.61 | [실패] 보수적 |
| 2 | Plus3 | 4개 | 34.69 | 27.66 | 9.77 | [실패] 과적합 |
| 3 | 조사 | 1개 | 33.47 | 31.91 | 11.54 | [실패] 특화 실패 |
| 3 | 띄어쓰기 | 1개 | 32.65 | - | - | [실패] 폐기 |
| 6 | 규칙 후처리 | - | 32.24 | - | - | [실패] 무효 |

---

## 재현 가이드

### 전체 재현 (모든 Phase)

```bash
# Phase 1: Baseline
uv run python scripts/run_experiment.py --prompt baseline

# Phase 2-1: Zero-shot
uv run python scripts/run_experiment.py --prompt zero_shot

# Phase 2-2: Plus3
uv run python scripts/run_experiment.py --prompt baseline_plus_3examples

# Phase 3-1: 조사
uv run python scripts/run_experiment.py --prompt baseline_josa

# Phase 6: 규칙 후처리
uv run python validate_baseline_minimal_rules.py
```

### 특정 Phase만 재현

**Baseline만 재현** (가장 빠름):
```bash
cd code
uv run python scripts/run_experiment.py --prompt baseline
```

**결과 확인**:
```bash
# Recall/Precision
cat outputs/logs/baseline_results.json

# LB 제출 파일
ls outputs/submissions/test/submission_baseline_test.csv
```

---

## 핵심 교훈 5가지

### 1. Few-shot의 양날의 검
- 1개 예시가 최적점
- 0개: 부족, 4개: 과잉

### 2. 예시 설계 > 예시 개수
- 단일 예시의 다양성이 중요
- 맞춤법 예시 (3가지 오류) > 조사 예시 (1가지)

### 3. Train 성능은 거짓말한다
- Train 향상 → Test 하락 (모든 실험)
- Train 기반 의사결정 불가능

### 4. Baseline의 진짜 한계
- 명확한 규칙: 이미 100% 처리
- 진짜 어려운 것: 맥락 이해, 주관적 판단

### 5. 최적점은 우연히 발견된다
- Baseline의 성공: 예시 설계 + 메타데이터 버그
- 완벽한 프롬프트를 찾는 것보다 다양한 시도와 검증

---

## 다음 단계 (시간 있을 시)

### 완전히 다른 접근
1. **System message 강화**
   - 출력 형식 제약 명시
   - 교정 범위 명확화

2. **JSON 구조화 출력**
   - 메타데이터 완전 제거
   - 파싱 오류 위험

3. **Multi-turn**
   - 오류 탐지 → 교정 분리
   - API 호출 2배, 토큰 증가

---

## 참고 자료

### 실험 결과 문서
- `outputs/analysis/FINAL_EXPERIMENT_SUMMARY.md`: Phase 1-5 종합
- `outputs/analysis/FAILURE_ANALYSIS_BASELINE_PLUS_3EXAMPLES.md`: Plus3 실패 분석
- `outputs/analysis/FINAL_MINIMAL_RULES_EXPERIMENT.md`: Phase 6 규칙 후처리

### 코드
- Baseline 프롬프트: `code/src/prompts/baseline.py`
- 실패한 프롬프트: `code/src/prompts/zero_shot.py`, `baseline_plus_3examples.py`, `baseline_josa.py`
- 규칙 후처리: `code/src/postprocessors/minimal_rule.py`

### 제출 파일
- 최종 선택: `outputs/submissions/test/submission_baseline_test_clean.csv` (34.04 / 13.45)
- Zero-shot: `submission_zero_shot_test.csv` (31.91 / 12.61)
- Plus3: `submission_baseline_plus_3examples_test.csv` (27.66 / 9.77)

---

**작성일**: 2025-10-24
**기반 문서**: tasks/tasks-prd-gec-prompt-optimization-system.md
**상태**: 전체 워크플로우 확정
