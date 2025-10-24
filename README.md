# 한국어 문법 교정 프롬프트 최적화
> Upstage GEC Promptathon 2024 | Team Red Legs

**"때로는 첫 시도가 최선이라는 겸손함을 배운 여정"**

---

## 프로젝트 개요

프롬프트 엔지니어링만으로 한국어 문법 교정 성능을 최대화하는 도전.

6단계(Phase 1-6)에 걸친 체계적 실험을 통해, Few-shot의 함정을 경험하고,
Train 성능과 Test 성능의 괴리를 목격하며,
결국 첫 번째 시도인 Baseline을 넘지 못했지만,
그 과정에서 얻은 인사이트가 더 가치 있었다.

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
- **5가지 핵심 인사이트** 도출

---

## 실패로부터의 교훈: 여정

### 출발점 (Phase 1)
254개 Train 데이터, Recall 최대화 목표로 시작.
첫 제출에서 **34.04%** 달성. 당시에는 개선할 여지가 많아 보였다.

### "더 많으면 더 좋지 않을까?" (Phase 2)

#### 실패 1: Zero-shot (예시 0개)
- 결과: **31.91%** (Baseline 대비 -2.13%p)
- 원인: 너무 보수적. False Negative 증가.
- 교훈: 최소 1개 예시는 필요함.

#### 실패 2: Plus3 (예시 4개)
- 결과: **27.66%** (Baseline 대비 -6.38%p, **18.7% 하락**)
- 충격적 발견: 긴 문장의 **첫 문장만 출력**하고 멈춤 (70-80% 텍스트 삭제)
- 원인: Few-shot 예시가 모두 짧은 단일 문장 → 모델이 길이 패턴 학습
- 교훈: **더 많은 예시 ≠ 더 좋은 성능**. 오히려 과적합.

### "특화하면 되지 않을까?" (Phase 3)

#### 실패 3: 조사 특화 예시
- Train: **33.47%** (+1.23%p 향상!)
- 기대: "Train에서 좋으니 Test도 좋겠지!"
- 결과:
  - Public: **31.91%** (-2.13%p)
  - Private: **11.54%** (최저 성적)
- 교훈: **Train 성능은 Test의 지표가 아니다.**

#### 실패 4: 띄어쓰기 예시
- Train: 32.65%, **길이 폭발 49개 (19.3%)**
- 즉시 폐기. LB 제출조차 안 함.
- 교훈: 예시 다양성 > 특화.

### 깨달음의 시간 (Phase 4-5)

**패턴 분석**:
```
예시 개수 vs LB 성능:
0개 (Zero-shot): 31.91% - 보수적
1개 (Baseline):  34.04% - 최적점 ⭐
4개 (Plus3):     27.66% - 과적합

Train vs Test 상관관계:
Plus3: Train 34.69% → Public 27.66% (-7.03%p) - 파국적 과적합
조사:  Train 33.47% → Public 31.91% (-1.56%p) - 일반화 실패
```

**핵심 발견**: Few-shot은 1개가 최적점. Train 성능 향상 = Test 성능 하락.

### 마지막 시도 (Phase 6)

#### 실패 5: 규칙 기반 후처리
- 전략: Train 데이터에서 명확한 패턴 추출 → 규칙으로 보정
- 추출 규칙: "금새→금세", "치 않→지 않", "추측컨대→추측건대" (100% 확실)
- 결과: **규칙 적용 0개**, Recall 32.24% (변화 없음)
- 원인: Baseline이 **이미 모두 교정**했음
- 깨달음: Baseline의 한계는 "규칙을 못 잡아서"가 아니라 "맥락 이해"가 필요한 부분

---

## 핵심 인사이트 5가지

### 1. Few-shot의 양날의 검
```
0개: 보수적 → FN 증가 → 31.91%
1개: 균형 → 최적점 → 34.04% ⭐
4개: 과적합 → 일반화 실패 → 27.66%
```
**교훈**: More is not always better. 예시 품질 > 예시 개수.

### 2. 예시 설계 > 예시 개수

**좋은 예시 (Baseline 맞춤법)**:
- 단 1개 예시에 **3가지 오류 유형** 포함
- 맞춤법, 띄어쓰기, 문법을 모두 커버
- 자연스러운 문장, 적절한 길이

**나쁜 예시 (Plus3)**:
- 4개 예시 모두 짧은 단일 문장 → 길이 편향
- 띄어쓰기 없음 → 띄어쓰기 교정 소홀
- 단순 패턴만 → 복잡한 케이스 실패

### 3. Train 성능은 거짓말한다

| 프롬프트 | Train | Public | Private | Train-Public 격차 |
|---------|-------|--------|---------|------------------|
| Baseline | 32.24 | **34.04** | 13.45 | **+1.80** (일반화 우수) ✅ |
| 조사 | **33.47** | 31.91 | **11.54** | **-1.56** (과적합) ❌ |
| Plus3 | **34.69** | 27.66 | 9.77 | **-7.03** (파국적 과적합) ❌ |

**교훈**: Train 성능 향상 = Test 성능 하락. Validation이 아니라 실제 Test만이 진실.

### 4. Baseline의 한계는 규칙이 아닌 이해력

**실험 전 생각**: "34%밖에 안 되는 건 명확한 규칙을 놓쳐서겠지?"

**실험 후 발견**:
- 명확한 규칙: 100% 처리
- "금새→금세", "치 않→지 않" 등 완벽 교정
- 규칙 추가 시도 → 적용 0개

**진짜 한계**:
- 복잡한 문맥 이해 필요
- 애매한 오류 (주관적 판단)
- 메타데이터 출력 제어 부족

### 5. 최적점은 우연히 발견된다

**Baseline 34.04%가 최고인 이유**:
1. 예시의 우수한 설계 (의도적? 우연?)
2. 1개 예시의 균형 (적절한 제약)
3. 메타데이터 버그가 오히려 도움 (4x 반복 출력 → TP 증가)

**의도적 설계가 아니었음**.

**교훈**: 완벽한 프롬프트를 찾으려는 집착보다, 다양한 시도와 검증이 중요.
그리고 **첫 시도가 최선일 수 있다**는 겸손.

---

## 실험 전체 요약

| Phase | 프롬프트 | 예시 | Train | Public | Private | 결과 | 실패 원인 |
|-------|---------|------|-------|--------|---------|------|-----------|
| 1 | **Baseline** | **1개** | 32.24 | **34.04** | **13.45** | ✅ **최고** | - |
| 2 | Zero-shot | 0개 | 32.24 | 31.91 | 12.61 | ❌ 보수적 | FN 증가 |
| 2 | Plus3 | 4개 | 34.69 | 27.66 | 9.77 | ❌ 파국 | 과적합, 길이 폭발, 첫 문장만 출력 |
| 3 | 조사 | 1개 (조사) | 33.47 | 31.91 | 11.54 | ❌ 특화 실패 | 일반화 실패, Private 최저 |
| 3 | 띄어쓰기 | 1개 (띄어쓰기) | 32.65 | - | - | ❌ 폐기 | 길이 폭발 49개 (19.3%) |
| 6 | 규칙 후처리 | - | 32.24 | - | - | ❌ 무효 | 규칙 적용 0개 (Baseline이 이미 처리) |

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
│   │   ├── prompts/        # 프롬프트 템플릿 (5개)
│   │   ├── metrics/        # 평가 지표
│   │   ├── postprocessors/ # 후처리
│   │   ├── generator.py
│   │   └── evaluator.py
│   ├── scripts/            # 실행 스크립트
│   ├── tests/              # 단위 테스트 (85개)
│   ├── data/               # Train/Test 데이터
│   └── outputs/            # 실험 결과
│       ├── submissions/    # 교정 결과 CSV
│       ├── logs/           # 평가 메트릭 JSON
│       └── analysis/       # 상세 분석
├── docs/                   # 문서
│   ├── 01_GETTING_STARTED.md       # 시작 가이드
│   ├── 02_EXPERIMENT_INSIGHTS.md   # 실험 인사이트 ⭐ 필독
│   ├── 03_TECHNICAL_DETAILS.md     # 기술 구현 상세
│   └── 04_COMPETITION_GUIDE.md     # 대회 정보
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
2. **[실험 인사이트](docs/02_EXPERIMENT_INSIGHTS.md)** ⭐ 필독
   - Phase 1-6 실험 여정
   - 실패 사례 심층 분석
   - 핵심 인사이트 5가지
   - 기술적 한계 및 교훈
3. **[기술 구현 상세](docs/03_TECHNICAL_DETAILS.md)** - 아키텍처 및 평가 지표
4. **[대회 정보](docs/04_COMPETITION_GUIDE.md)** - 규칙 및 데이터셋

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

---

## 후기

### 배운 것

완벽한 프롬프트를 찾는 여정이 아니라,
**최적점이 어디인지, 왜 그런지 이해하는 과정**이었다.

그리고 때로는 **첫 시도가 최선**이라는 겸손함을 배웠다.

### 숫자의 의미

34.04%는 단순한 숫자가 아니라,
20번의 제출 중 4번을 사용해 얻은 **교훈의 집합**이다.

### 실패의 가치

- Plus3 실패 → Few-shot 과적합 메커니즘 이해
- 조사 실패 → Train 성능 무의미성 발견
- 규칙 실패 → Baseline의 진짜 한계 파악

**실패가 인사이트를 만들었다.**

---

## 참고 자료

### 프로젝트

- **실험 인사이트**: [docs/02_EXPERIMENT_INSIGHTS.md](docs/02_EXPERIMENT_INSIGHTS.md) ⭐ 필독
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

**프로젝트 기간**: 2024년 10월 ~
**최종 성과**: Public 34.04% / Private 13.45%
**핵심 교훈**: 첫 시도가 최선일 수 있다는 겸손함

**마지막 업데이트**: 2025-10-24
**구조 개편**: 포트폴리오용 리팩토링 완료
