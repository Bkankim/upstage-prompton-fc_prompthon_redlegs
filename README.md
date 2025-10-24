# 한국어 문법 교정 프롬프트 최적화
> Upstage GEC Promptathon 2025 | Team Red Legs (1인팀)

프롬프트 엔지니어링만으로 한국어 문법 교정 성능을 최대화하는 프로젝트입니다.

---

## 프로젝트 개요

6단계(Phase 1-6)에 걸친 체계적인 실험을 통해 Few-shot 학습의 한계를 확인하고, Train/Test 성능 격차의 원인을 분석했습니다. 20개 이상의 프롬프트 변형을 시도한 결과, 첫 번째 시도인 Baseline(예시 1개)이 최고 성능을 기록했으며, 이를 통해 프롬프트 설계에 대한 핵심 인사이트를 도출했습니다.

**프로젝트 제약사항**: 대회 기간 중 컨디션 문제로 실제 작업 기간이 이틀로 제한되어, 앙상블 전략, 체인 오브 씽킹, 다단계 교정 등 더 다양한 프롬프트 기법을 실험하지 못했습니다.

---

## 성과

### 최종 결과
- **Public LB**: 34.0426%
- **Private LB**: 13.4454%
- **프롬프트**: Baseline (맞춤법 예시 1개)
- **제출 사용**: 4회 / 20회

### 실험 범위
- **6개 Phase** 완료 (Phase 1-6)
- **20+ 프롬프트 변형** 시도
- **핵심 인사이트** 도출

---

## 실험 과정

### Phase 1: 기준선 설정
254개 Train 데이터로 Recall 최대화를 목표로 시작했습니다.
맞춤법 예시 1개를 포함한 Baseline 프롬프트로 **34.04%** 달성.

### Phase 2: 예시 개수 변화 실험

#### 실험 1: Zero-shot (예시 0개)
- 결과: **31.91%** (Baseline 대비 -2.13%p)
- 원인: 너무 보수적. False Negative 증가
- 최소 1개 예시는 필요함을 확인

#### 실험 2: Plus3 (예시 4개)
- 결과: **27.66%** (Baseline 대비 -6.38%p, **18.7% 하락**)
- 주요 문제: 긴 문장의 **첫 문장만 출력**하고 멈춤 (70-80% 텍스트 삭제)
- 원인: Few-shot 예시가 모두 짧은 단일 문장 → 모델이 길이 패턴 학습
- 결론: **더 많은 예시 ≠ 더 좋은 성능**

### Phase 3: 예시 특화 실험

#### 실험 3: 조사 특화 예시
- Train: **33.47%** (+1.23%p 향상)
- Public: **31.91%** (-2.13%p)
- Private: **11.54%** (최저 성적)
- 결론: Train 성능 향상이 Test 성능 향상을 보장하지 않음

#### 실험 4: 띄어쓰기 특화 예시
- Train: 32.65%, **길이 폭발 49개 (19.3%)**
- LB 제출 없이 즉시 폐기
- 결론: 특화된 예시보다 다양한 예시가 중요

### Phase 4-5: 중간 분석

**패턴 분석 결과**:
```
예시 개수 vs LB 성능:
0개 (Zero-shot): 31.91% - 보수적
1개 (Baseline):  34.04% - 최적점 [중요]
4개 (Plus3):     27.66% - 과적합

Train vs Test 상관관계:
Plus3: Train 34.69% → Public 27.66% (-7.03%p) - 파국적 과적합
조사:  Train 33.47% → Public 31.91% (-1.56%p) - 일반화 실패
```

**결론**: Few-shot 예시는 1개가 최적점. Train 성능 향상 시 Test 성능은 오히려 하락.

### Phase 6: 규칙 기반 후처리

#### 실험 5: 명확한 패턴 규칙화
- 전략: Train 데이터에서 100% 확실한 패턴 추출 → 규칙으로 보정
- 추출 규칙: "금새→금세", "치 않→지 않", "추측컨대→추측건대"
- 결과: **규칙 적용 0개**, Recall 32.24% (변화 없음)
- 원인: Baseline이 **이미 모두 교정**했음
- 결론: Baseline의 한계는 규칙 처리 능력이 아닌 맥락 이해력

---

## 핵심 인사이트

### 1. Few-shot 예시 개수의 최적점
```
0개: 보수적 → FN 증가 → 31.91%
1개: 균형 → 최적점 → 34.04% [중요]
4개: 과적합 → 일반화 실패 → 27.66%
```
More is not always better. 예시 개수보다 **예시 품질**이 중요합니다.

### 2. 좋은 예시의 조건

**좋은 예시 (Baseline)**:
- 단 1개 예시에 **3가지 오류 유형** 포함
- 맞춤법, 띄어쓰기, 문법을 모두 커버
- 자연스러운 문장, 적절한 길이

**나쁜 예시 (Plus3)**:
- 4개 예시 모두 짧은 단일 문장 → 길이 편향 발생
- 띄어쓰기 예시 없음 → 띄어쓰기 교정 소홀
- 단순 패턴만 반복 → 복잡한 케이스 실패

### 3. Train 성능과 Test 성능의 괴리

| 프롬프트 | Train | Public | Private | Train-Public 격차 |
|---------|-------|--------|---------|------------------|
| Baseline | 32.24 | **34.04** | 13.45 | **+1.80** (일반화 우수) [완료] |
| 조사 | **33.47** | 31.91 | **11.54** | **-1.56** (과적합) [실패] |
| Plus3 | **34.69** | 27.66 | 9.77 | **-7.03** (파국적 과적합) [실패] |

Train에서 성능이 높을수록 Test에서는 오히려 하락했습니다. Validation이 없는 환경에서는 실제 Test만이 진실입니다.

### 4. Baseline의 실제 한계

**가설**: "34%밖에 안 나오는 건 명확한 규칙을 못 잡아서겠지?"

**실험 결과**:
- 명확한 규칙: 100% 처리 완료
- "금새→금세", "치 않→지 않" 등 완벽 교정
- 규칙 추가 시도 → 적용 0개

**실제 한계**:
- 복잡한 문맥 이해 필요
- 애매한 오류 (주관적 판단 필요)
- 메타데이터 출력 제어 부족

### 5. 최적 프롬프트 발견의 우연성

**Baseline이 최고 성능을 보인 이유**:
1. 예시에 3가지 오류 유형이 균형있게 포함됨
2. 1개 예시가 적절한 제약으로 작용
3. 메타데이터 반복 출력이 의도치 않게 TP 증가에 기여

체계적 설계의 결과가 아니라 초기 시도의 우연한 균형이었습니다. 완벽한 프롬프트를 찾으려는 집착보다 **다양한 시도와 검증**이 더 중요합니다.

---

## 실험 전체 요약

| Phase | 프롬프트 | 예시 | Train | Public | Private | 결과 | 실패 원인 |
|-------|---------|------|-------|--------|---------|------|-----------|
| 1 | **Baseline** | **1개** | 32.24 | **34.04** | **13.45** | [완료] **최고** | - |
| 2 | Zero-shot | 0개 | 32.24 | 31.91 | 12.61 | [실패] 보수적 | FN 증가 |
| 2 | Plus3 | 4개 | 34.69 | 27.66 | 9.77 | [실패] 파국 | 과적합, 길이 폭발, 첫 문장만 출력 |
| 3 | 조사 | 1개 (조사) | 33.47 | 31.91 | 11.54 | [실패] 특화 실패 | 일반화 실패, Private 최저 |
| 3 | 띄어쓰기 | 1개 (띄어쓰기) | 32.65 | - | - | [실패] 폐기 | 길이 폭발 49개 (19.3%) |
| 6 | 규칙 후처리 | - | 32.24 | - | - | [실패] 무효 | 규칙 적용 0개 (Baseline이 이미 처리) |

---

## 기술 스택

### 환경
- **Python**: 3.12
- **패키지 관리**: uv
- **모델**: Upstage Solar Pro 2 (파인튜닝 불가, 프롬프트만)

### 아키텍처
```
Input (오류 문장)
  ↓
Prompt Template (System + User + Few-shot)
  ↓
Upstage Solar Pro 2 API (최대 3회 호출)
  ↓
Postprocessor (메타데이터 제거, 선택적)
  ↓
Evaluator (LCS 기반 Recall 계산)
  ↓
Output (교정 문장 + 메트릭)
```

### 핵심 컴포넌트
- **Prompts** (`src/prompts/`): Baseline, Zero-shot, Plus3, 조사 특화 (5개)
- **Generator** (`src/generator.py`): API 호출 및 교정 생성
- **Evaluator** (`src/metrics/evaluator.py`): LCS 기반 Recall/Precision 계산
- **Postprocessors** (`src/postprocessors/`): 메타데이터 제거, 규칙 기반 후처리

---

## 프로젝트 구조

```
├── code/                   # 핵심 코드
│   ├── src/                # 소스 모듈
│   │   ├── prompts/        # 프롬프트 템플릿 (4개)
│   │   ├── metrics/        # 평가 지표
│   │   ├── postprocessors/ # 후처리
│   │   ├── generator.py
│   │   └── evaluator.py
│   ├── scripts/            # 실행 스크립트
│   ├── tests/              # 단위 테스트
│   ├── data/               # Train/Test 데이터
│   └── outputs/            # 실험 결과
│       ├── submissions/    # 교정 결과 CSV
│       ├── logs/           # 평가 메트릭 JSON
│       └── analysis/       # 상세 분석
├── docs/                   # 문서
│   ├── 01_GETTING_STARTED.md       # 시작 가이드
│   ├── 02_EXPERIMENT_INSIGHTS.md   # 실험 인사이트 [중요] 필독
│   ├── 03_TECHNICAL_DETAILS.md     # 기술 구현 상세
│   ├── 04_COMPETITION_GUIDE.md     # 대회 정보
│   └── 05_WORKFLOW.md              # 실험 워크플로우
├── outputs/                # 실험 결과 아카이브
│   ├── analysis/           # 핵심 분석 문서 (3개)
│   └── logs/               # 실험 로그 요약
└── README.md               # 이 파일
```

---

## 빠른 시작

### 환경 설정

```bash
# 1. uv 설치
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. 프로젝트 클론 및 의존성 설치
cd code
uv sync

# 3. API 키 설정
echo "UPSTAGE_API_KEY=your_key" > .env
```

### Baseline 재현

```bash
# Train 교정 + 평가 + Test 생성 (통합)
uv run python scripts/run_experiment.py --prompt baseline

# 결과 확인
cat outputs/logs/baseline_results.json
# {"recall": 32.24, "precision": 14.79}
```

**중요**: 모든 Python 실행은 반드시 `uv run` 사용!

---

## 문서

### 필독 문서 (읽기 순서)

1. **[시작하기](docs/01_GETTING_STARTED.md)** - 환경 설정 및 재현
2. **[실험 인사이트](docs/02_EXPERIMENT_INSIGHTS.md)** [중요] 필독
   - Phase 1-6 실험 여정
   - 실패 사례 심층 분석
   - 핵심 인사이트
   - 기술적 한계 및 교훈
3. **[기술 구현 상세](docs/03_TECHNICAL_DETAILS.md)** - 아키텍처 및 평가 지표
4. **[대회 정보](docs/04_COMPETITION_GUIDE.md)** - 규칙 및 데이터셋
5. **[실험 워크플로우](docs/05_WORKFLOW.md)** - Phase 1-6 재현 가이드

### 상세 분석 문서

- `outputs/analysis/FINAL_EXPERIMENT_SUMMARY.md`: Phase 1-5 종합 분석
- `outputs/analysis/FAILURE_ANALYSIS_BASELINE_PLUS_3EXAMPLES.md`: Plus3 실패 분석
- `outputs/analysis/FINAL_MINIMAL_RULES_EXPERIMENT.md`: Phase 6 규칙 후처리

### 코드 문서

- `code/README.md`: 코드 구조 및 사용법
- `outputs/README.md`: 실험 결과 가이드

---

## 기술적 한계 및 극복 시도

### 한계 1: Public/Private 격차 20%p

**현상**: 모든 실험에서 일관되게 발생
```
Baseline: 34.04% → 13.45% (-20.59%p)
Zero-shot: 31.91% → 12.61% (-19.30%p)
Plus3: 27.66% → 9.77% (-17.89%p)
```

**원인 추정**: 데이터 분포 차이 (구조적 문제)
**시도한 극복**: 일반화 전략, 보수적 접근
**결과**: 모두 실패. 프롬프트로 해결 불가.

### 한계 2: 메타데이터 출력 제어

**현상**: Baseline 5개 케이스에서 메타데이터 포함 ("[수정 보완]", "최종 출력:" 등)
**시도한 극복**: RuleChecklist postprocessor (정규식 제거)
**결과**: 일부만 제거
**역설**: 제거하면 점수 하락 가능성 (메타데이터 반복이 TP 증가에 기여)

### 한계 3: 제한된 실험 기간

**현상**: 컨디션 문제로 실제 작업 기간 이틀
**시도하지 못한 실험**:
- 앙상블 전략 (다중 프롬프트 결과 투표)
- 체인 오브 씽킹 (단계별 오류 분석)
- 다단계 교정 (1차 교정 → 2차 검증)
- 도메인별 프롬프트 (문법/맞춤법/띄어쓰기 분리)
- Self-consistency (같은 프롬프트 여러 번 실행)

**향후 가능성**: 충분한 시간이 주어진다면 더 다양한 프롬프트 엔지니어링 기법 탐색 가능

---

## 참고 자료

### 프로젝트

- **실험 인사이트**: [docs/02_EXPERIMENT_INSIGHTS.md](docs/02_EXPERIMENT_INSIGHTS.md) [중요] 필독
- **코드 구조**: [code/README.md](code/README.md)
- **실험 결과**: [outputs/README.md](outputs/README.md)

### 외부

- **Upstage Solar Pro 2**: https://console.upstage.ai/docs
- **대회 페이지**: (링크)
- **uv 패키지 관리자**: https://github.com/astral-sh/uv

---

## 라이센스 및 크레딧

- **Team**: Red Legs
- **대회**: Upstage Global Eval Challenge (GEC) - Promptathon 2024
- **모델**: Upstage Solar Pro 2

---

**프로젝트 기간**: 2025년 10월 20일 ~ 24일 (실제 작업 기간: 2일)
**최종 성과**: Public 34.04% / Private 13.45%
**제출 사용**: 4회 / 20회

**마지막 업데이트**: 2025-10-24
