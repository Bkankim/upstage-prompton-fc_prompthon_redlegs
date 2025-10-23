# 문장 생성기 통합 아키텍처

## 개요

기존 3개의 중복된 생성 스크립트(baseline_generate.py, fewshot_v2_generate.py, errortypes_v3_generate.py)를 통합 생성기 구조로 리팩토링했습니다.

## 파일 구조

```
code/
├── src/
│   └── generator.py              # 통합 생성기 클래스 (157줄)
├── scripts/
│   └── generate.py               # 통합 실행 스크립트 (95줄)
├── baseline_generate.py          # 레거시 래퍼 (43줄)
├── fewshot_v2_generate.py        # 레거시 래퍼 (44줄)
└── errortypes_v3_generate.py     # 레거시 래퍼 (44줄)
```

## 주요 변경 사항

### 1. SentenceGenerator 클래스 (src/generator.py)

프롬프트 레지스트리를 활용한 통합 생성기:

```python
class SentenceGenerator:
    def __init__(self, prompt_name: str, model: str = "solar-pro2", api_key: Optional[str] = None)
    def generate_single(self, text: str) -> str
    def generate_batch(self, err_sentences: List[str]) -> pd.DataFrame
    def generate_from_csv(self, input_path: str, output_path: str) -> None
```

**특징:**
- 프롬프트 레지스트리에서 자동 조회
- OpenAI 클라이언트 초기화 (Upstage API)
- 예외 처리 및 fallback
- tqdm 진행 표시

### 2. 통합 실행 스크립트 (scripts/generate.py)

모든 프롬프트를 실행할 수 있는 범용 스크립트:

```bash
# 사용 예시
uv run python scripts/generate.py --prompt baseline --input data/train.csv --output outputs/baseline.csv
uv run python scripts/generate.py --prompt fewshot_v2 --input data/test.csv --output outputs/fewshot.csv
uv run python scripts/generate.py --list-prompts
```

**특징:**
- --prompt 인자로 프롬프트 선택
- --list-prompts로 사용 가능한 프롬프트 목록 확인
- sys.path 조정으로 src 모듈 import 지원

### 3. 레거시 래퍼

기존 스크립트 호출 방식을 그대로 유지:

```bash
# 기존 방식 그대로 동작
uv run python baseline_generate.py --input data/train.csv --output submission.csv
uv run python fewshot_v2_generate.py --input data/train.csv --output submission_fewshot.csv
uv run python errortypes_v3_generate.py --input data/train.csv --output submission_errors.csv
```

**구현 방식:**
- subprocess로 scripts/generate.py 호출
- 프롬프트 이름만 다르게 전달
- 인자는 그대로 전달

## 코드 중복 제거 효과

### 기존 구조
- baseline_generate.py: 68줄
- fewshot_v2_generate.py: 71줄
- errortypes_v3_generate.py: 72줄
- **총 211줄 (대부분 중복)**

### 새 구조
- **핵심 로직:** generator.py(157줄) + generate.py(95줄) = 252줄
- **래퍼:** 3개 × 약 43줄 = 131줄
- **총 383줄 (중복 없음)**

### 효과
1. **중복 제거:** 3개 스크립트의 95% 중복 코드 → 단일 구현
2. **유지보수성:** 버그 수정이나 개선 시 한 곳만 수정
3. **확장성:** 새 프롬프트 추가 시 레지스트리만 업데이트
4. **하위 호환성:** 기존 스크립트 호출 방식 유지

## 검증 결과

### 테스트 내용
- 1개 샘플로 통합 스크립트와 레거시 래퍼 실행
- baseline과 fewshot_v2 프롬프트 검증

### 결과
- ✅ 통합 스크립트 정상 동작
- ✅ 레거시 래퍼 정상 동작
- ✅ 출력 결과 동일
- ✅ API 호출 및 에러 처리 정상

## 사용 가이드

### 새로운 프롬프트 추가 방법

1. 프롬프트 클래스 작성 (src/prompts/new_prompt.py)
2. 레지스트리에 등록 (src/prompts/registry.py의 register_default_prompts)
3. 통합 스크립트로 바로 사용 가능:
   ```bash
   uv run python scripts/generate.py --prompt new_prompt --input data/train.csv --output output.csv
   ```

4. (선택) 레거시 래퍼 추가:
   ```python
   # new_prompt_generate.py
   subprocess.run([sys.executable, "scripts/generate.py", "--prompt", "new_prompt", ...])
   ```

### 권장 사용 방법

**일반 사용:**
```bash
uv run python scripts/generate.py --prompt <prompt_name> --input <input_file> --output <output_file>
```

**기존 워크플로우 유지:**
```bash
uv run python baseline_generate.py --input data/train.csv --output submission.csv
```

## 향후 개선 방향

1. **배치 처리 최적화**
   - 비동기 API 호출 지원
   - 병렬 처리 옵션 추가

2. **캐싱**
   - 동일 입력에 대한 결과 캐싱
   - API 호출 비용 절감

3. **로깅**
   - 실험 로그 자동 저장
   - 성능 메트릭 수집

4. **CLI 개선**
   - 더 풍부한 옵션 지원
   - 설정 파일 지원

## 기술 스택

- **프롬프트 관리:** src/prompts/registry 시스템
- **API 클라이언트:** OpenAI SDK (Upstage API)
- **환경 관리:** python-dotenv
- **진행 표시:** tqdm
- **데이터 처리:** pandas

## 문의

구조 개선이나 버그 발견 시 이슈 등록 또는 문서 업데이트 부탁드립니다.
