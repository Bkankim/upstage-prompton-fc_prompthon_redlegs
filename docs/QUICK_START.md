# 빠른 시작 가이드 (Quick Start)

> 5분 안에 첫 실험 시작하기

## 0) 사전 요구사항

- Python 3.12+
- Git
- UV 패키지 관리자
- Upstage API 키

---

## 1) 환경 설정 (3단계, 2분)

### Step 1: 프로젝트 클론
```bash
git clone <repository-url>
cd upstage-prompton-fc_prompthon_redlegs
```

### Step 2: UV 설치 (없는 경우)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Step 3: 의존성 설치 및 API 키 설정
```bash
cd code

# 의존성 설치
uv sync

# API 키 설정
echo "UPSTAGE_API_KEY=your_key_here" > .env
```

---

## 2) 첫 실험 실행 (1개 명령어, 2분)

### Baseline 실험 (이미 완료됨)
```bash
# Baseline 프롬프트로 Train 데이터 교정
uv run python scripts/run_experiment.py --prompt baseline
```

**결과 확인**:
- Train 교정 파일: `code/outputs/submissions/train/submission_baseline.csv`
- Test 제출 파일: `code/outputs/submissions/test/submission_baseline_test.csv`
- 평가 결과: `code/outputs/logs/baseline_results.json`
- 상세 분석: `code/outputs/analysis/analysis_baseline.csv`

---

## 3) 결과 확인 (30초)

### 성능 메트릭 확인
```bash
# JSON 로그 확인
cat code/outputs/logs/baseline_results.json
```

**예상 출력**:
```json
{
  "prompt": "baseline",
  "train_performance": {
    "recall": 32.24,
    "precision": 14.79
  },
  "timestamp": "2025-10-22T..."
}
```

### LB 제출 파일 확인
```bash
# 제출 파일 위치
ls -lh code/outputs/submissions/test/submission_baseline_test.csv

# 파일 내용 미리보기
head -5 code/outputs/submissions/test/submission_baseline_test.csv
```

---

## 4) 다음 스텝

### 4.1 Rule-Checklist 적용 (즉시, 30분)

**가장 빠른 개선!** 국립국어원 규칙 기반 후처리

```bash
# 1. utils/rule_checklist.py 생성 (docs/ADVANCED_STRATEGIES.md 참고)
# 2. Baseline에 Rule-Checklist 적용
uv run python scripts/run_experiment.py --prompt baseline_rulechecklist
```

**예상 효과**: +2-3%p → 36-37% Recall

### 4.2 CD-CoT 프롬프트 실험 (최우선, 2시간)

**최고 ROI!** 2024년 +17.8% 검증된 기법

```bash
# 1. prompts/cd_cot.py 생성 (docs/ADVANCED_STRATEGIES.md 참고)
# 2. CD-CoT 실험
uv run python scripts/run_experiment.py --prompt cd_cot
```

**예상 효과**: +10-15%p → 46-52% Recall

### 4.3 LB 제출 및 결과 비교

```bash
# 1. 제출 파일 찾기
ls code/outputs/submissions/test/*_test.csv

# 2. LB에 제출 (웹사이트)
# 3. 결과 기록
echo "cd_cot LB Recall: XX.XX%" >> code/outputs/logs/lb_results.txt
```

---

## 5) 자주 사용하는 명령어

### 실험 실행
```bash
# 특정 프롬프트로 전체 워크플로우 (교정 + 평가 + 제출 파일 생성)
uv run python scripts/run_experiment.py --prompt {prompt_name}

# 교정만 실행
uv run python scripts/generate.py --prompt {prompt_name}

# 평가만 실행
uv run python scripts/evaluate.py
```

### 결과 확인
```bash
# 모든 실험 결과 요약
cat code/outputs/logs/*_results.json | grep recall

# 특정 프롬프트 결과
cat code/outputs/logs/{prompt_name}_results.json

# 오류 유형별 분석
cat code/outputs/analysis/analysis_{prompt_name}.csv
```

### 파일 관리
```bash
# 제출 파일 목록
ls -lh code/outputs/submissions/test/*.csv

# 실험 로그 목록
ls -lh code/outputs/logs/*.json

# 디스크 사용량 확인 (150GB 한도)
du -sh code/outputs/
```

---

## 6) 문제 해결

### UV 환경 오류
```bash
# UV 재동기화
cd code && uv sync

# Python 버전 확인
uv run python --version  # Python 3.12+

# 환경 정리
rm -rf .venv && uv sync
```

### API 키 오류
```bash
# API 키 확인
cat code/.env

# API 키 재설정
echo "UPSTAGE_API_KEY=your_new_key" > code/.env
```

### 파일 경로 오류
```bash
# 데이터 파일 확인
ls code/data/*.csv

# 출력 디렉토리 생성
mkdir -p code/outputs/{submissions/train,submissions/test,logs,analysis}
```

---

## 7) 추가 학습 자료

### 필수 문서 (순서대로 읽기)
1. `README.md` - 프로젝트 개요
2. `CLAUDE.md` - 필수 규칙 및 워크플로우
3. `docs/ADVANCED_STRATEGIES.md` - **최신 기법 가이드** ⭐
4. `docs/EXPERIMENT_LESSONS.md` - 과적합 교훈
5. `code/outputs/logs/submission_guide.md` - 제출 전략

### 대회 공식 문서
- `docs/overview_agents.md` - 대회 가이드
- `docs/evaluation.md` - 평가 방식
- `docs/datasetguide.md` - 데이터셋 가이드

### 코드 문서
- `code/README.md` - 코드 사용법
- `code/docs/GENERATOR_ARCHITECTURE.md` - 아키텍처
- `docs/UV_ENVIRONMENT_GUIDE.md` - UV 환경 상세

---

## 8) 빠른 체크리스트

### 환경 설정 완료 확인
- [ ] UV 설치 완료 (`uv --version` 확인)
- [ ] 의존성 설치 완료 (`cd code && uv sync`)
- [ ] API 키 설정 완료 (`cat code/.env`)
- [ ] 데이터 파일 존재 (`ls code/data/train_dataset.csv`)

### 첫 실험 완료 확인
- [ ] Baseline 교정 완료
- [ ] Train 평가 완료 (Recall: 32.24%)
- [ ] Test 제출 파일 생성 완료
- [ ] 결과 JSON 로그 확인

### 다음 실험 준비
- [ ] `docs/ADVANCED_STRATEGIES.md` 읽기
- [ ] Rule-Checklist 또는 CD-CoT 선택
- [ ] 프롬프트 코드 작성 계획

---

## 9) 도움 받기

### 문서 참조
```bash
# UV 환경 가이드
cat docs/UV_ENVIRONMENT_GUIDE.md

# 베이스라인 코드 가이드
cat docs/BASELINE_CODE.md

# 제출 가이드
cat code/outputs/logs/submission_guide.md
```

### 커뮤니티
- GitHub Issues: 버그 리포트 및 질문
- 대회 포럼: 공식 Q&A

---

**다음 단계**: `docs/ADVANCED_STRATEGIES.md`를 읽고 Rule-Checklist 또는 CD-CoT 구현하기!

**목표**: 현재 34.04% → 50% Recall 달성!