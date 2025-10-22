# UV 환경 필수 사용 지침

**⚠️ 중요: 모든 실험은 반드시 uv 환경에서 실행해야 합니다**

---

## 📌 왜 uv를 사용해야 하는가?

1. **의존성 관리 일관성**: pyproject.toml에 정의된 정확한 패키지 버전 사용
2. **Python 버전 고정**: Python 3.12 환경 보장
3. **재현성 보장**: 모든 실험 결과의 일관된 재현
4. **격리된 환경**: 시스템 Python과 충돌 방지

---

## 🚨 필수 규칙

### ❌ 절대 하지 말아야 할 것
```bash
# 잘못된 실행 방법들 - 사용 금지!
python baseline_generate.py        # ❌ 시스템 Python 사용
python3 evaluate.py                # ❌ 시스템 Python 사용
pip install pandas                 # ❌ pip 직접 사용
conda activate myenv              # ❌ 다른 환경 사용
```

### ✅ 반드시 이렇게 실행
```bash
# 올바른 실행 방법 - uv 사용!
uv run python baseline_generate.py  # ✅ uv 환경에서 실행
uv run python evaluate.py           # ✅ uv 환경에서 실행
uv pip install pandas               # ✅ uv로 패키지 설치
uv sync                             # ✅ 의존성 동기화
```

---

## 🔧 초기 설정 (한 번만)

### 1. uv 설치
```bash
# uv가 없는 경우에만
curl -LsSf https://astral.sh/uv/install.sh | sh

# 설치 확인
uv --version
```

### 2. 프로젝트 디렉토리로 이동
```bash
cd /Competition/upstage-prompton-fc_prompthon_redlegs/code
```

### 3. 의존성 설치
```bash
# pyproject.toml 기반으로 자동 설치
uv sync
```

### 4. API 키 설정
```bash
# .env 파일 생성 (아직 없는 경우)
echo "UPSTAGE_API_KEY=your_actual_api_key_here" > .env
```

---

## 🚀 실행 가이드

### 베이스라인 실행
```bash
# 반드시 code 디렉토리에서
cd /Competition/upstage-prompton-fc_prompthon_redlegs/code

# 1. 교정 실행 (uv run 필수!)
uv run python baseline_generate.py

# 2. 평가 실행 (uv run 필수!)
uv run python evaluate.py
```

### 데이터 분석 실행
```bash
# uv run 필수!
uv run python analyze_dataset.py
```

### 새 스크립트 실행
```bash
# 어떤 Python 스크립트든 uv run으로 실행
uv run python your_new_script.py
```

---

## 📦 패키지 관리

### 새 패키지 추가
```bash
# uv를 통해 추가 (pyproject.toml 자동 업데이트)
uv add numpy
uv add scikit-learn
```

### 패키지 제거
```bash
# uv를 통해 제거
uv remove package_name
```

### 의존성 업데이트
```bash
# 모든 패키지 최신 버전으로
uv sync --upgrade
```

---

## 🔍 환경 확인

### Python 버전 확인
```bash
# uv 환경의 Python 버전
uv run python --version
# 출력: Python 3.12.x
```

### 설치된 패키지 확인
```bash
# uv 환경의 패키지 목록
uv pip list
```

### 환경 위치 확인
```bash
# .venv 디렉토리 확인
ls -la .venv/
```

---

## ⚠️ 트러블슈팅

### 문제 1: uv 명령을 찾을 수 없음
```bash
# 해결: uv 재설치
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc  # 또는 ~/.zshrc
```

### 문제 2: 의존성 설치 실패
```bash
# 해결: 캐시 정리 후 재시도
uv cache clean
uv sync
```

### 문제 3: Python 버전 불일치
```bash
# 해결: .python-version 확인
cat .python-version  # 3.12 확인
uv python install 3.12  # 필요시 설치
```

### 문제 4: 패키지 import 에러
```bash
# 해결: uv run을 사용했는지 확인
# 잘못된 방법
python script.py  # ❌

# 올바른 방법
uv run python script.py  # ✅
```

---

## 📋 체크리스트

실험 시작 전 확인사항:

- [ ] uv 설치 완료 (`uv --version`)
- [ ] code 디렉토리에 있음 (`pwd`로 확인)
- [ ] `uv sync` 실행 완료
- [ ] `.env` 파일에 API 키 설정
- [ ] 모든 스크립트는 `uv run python`으로 실행

---

## 🎯 핵심 요약

### 기억해야 할 단 하나의 규칙:

```bash
# 모든 Python 실행은 반드시 uv run을 앞에 붙인다!
uv run python [스크립트명].py
```

**이유**:
- 정확한 Python 버전 (3.12) 사용
- 정확한 패키지 버전 사용
- 실험 재현성 보장
- 의존성 충돌 방지

---

## 📚 참고 자료

- uv 공식 문서: https://github.com/astral-sh/uv
- pyproject.toml 위치: `/Competition/upstage-prompton-fc_prompthon_redlegs/code/pyproject.toml`
- Python 버전: 3.12 (.python-version 파일 참조)

---

**작성일**: 2024년 10월 22일
**중요도**: 🔴 **필수** - 반드시 준수