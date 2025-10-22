## Relevant Files

- `code/prompts.py` - 프롬프트 템플릿 정의 (핵심 수정 대상)
- `code/baseline_generate.py` - 교정 문장 생성 실행 스크립트
- `code/evaluate.py` - 평가 메트릭 계산 실행 스크립트
- `code/metrics.py` - Recall/Precision 계산 로직
- `code/analyze_dataset.py` - 데이터셋 오류 패턴 분석 도구
- `code/experiments/prompt_manager.py` - 프롬프트 버전 관리 시스템 (생성 예정)
- `code/experiments/batch_runner.py` - 배치 실험 실행기 (생성 예정)
- `code/experiments/result_analyzer.py` - 실험 결과 분석기 (생성 예정)
- `code/experiments/optimizer.py` - 최적 템플릿 선택기 (생성 예정)
- `code/experiments/submission_generator.py` - 최종 제출 파일 생성기 (생성 예정)
- `logs/` - 실험 로그 저장 디렉토리 (생성 예정)
- `submissions/` - 제출 파일 저장 디렉토리 (생성 예정)

### Notes

- **⚠️ 중요: 모든 Python 실행은 반드시 `uv run python` 명령 사용**
- 베이스라인 코드는 이미 `/code` 폴더에 준비되어 있음
- uv를 사용한 의존성 관리 (pyproject.toml)
- Python 3.12 사용 (.python-version)
- 실험은 베이스라인 성능 측정부터 시작하여 점진적으로 개선
- 모든 실험 결과는 JSON 형식으로 로깅
- 상세 uv 가이드: `/docs/UV_ENVIRONMENT_GUIDE.md`

## Tasks

- [ ] 1.0 베이스라인 성능 측정 및 분석
  - [ ] 1.1 환경 설정 및 의존성 설치 확인 (uv sync)
  - [ ] 1.2 API 키 설정 확인 (.env 파일)
  - [ ] 1.3 데이터 파일 배치 확인 (code/data/train_dataset.csv)
  - [ ] 1.4 베이스라인 프롬프트로 교정 실행 (baseline_generate.py)
  - [ ] 1.5 베이스라인 Recall 점수 측정 (evaluate.py)
  - [ ] 1.6 오류 유형별 분석 결과 검토 (analysis.csv)
  - [ ] 1.7 베이스라인 성능 문서화 (logs/baseline_results.json)

- [ ] 2.0 프롬프트 개선 전략 실험
  - [ ] 2.1 Few-shot 예시 추가 버전 작성 (prompts_v2_fewshot.py)
  - [ ] 2.2 오류 유형 명시 버전 작성 (prompts_v3_errortypes.py)
  - [ ] 2.3 Chain-of-Thought 버전 작성 (prompts_v4_cot.py)
  - [ ] 2.4 Multi-turn 검증 버전 작성 (prompts_v5_multiturn.py)
  - [ ] 2.5 각 버전별 성능 측정 및 비교
  - [ ] 2.6 최적 프롬프트 전략 선택

- [ ] 3.0 실험 자동화 시스템 구축
  - [ ] 3.1 프롬프트 버전 관리 시스템 개발 (prompt_manager.py)
  - [ ] 3.2 배치 실험 실행기 구현 (batch_runner.py)
  - [ ] 3.3 실험 로그 저장 시스템 구현 (JSON 형식)
  - [ ] 3.4 체크포인트 및 재시작 기능 추가
  - [ ] 3.5 토큰 제한 모니터링 시스템 구현
  - [ ] 3.6 API 호출 제한 관리 시스템 구현

- [ ] 4.0 최적화 및 분석 시스템 개발
  - [ ] 4.1 실험 결과 분석기 개발 (result_analyzer.py)
  - [ ] 4.2 오류 유형별 성능 매트릭스 생성
  - [ ] 4.3 최적 템플릿 자동 선택기 구현 (optimizer.py)
  - [ ] 4.4 오류 패턴별 프롬프트 추천 시스템
  - [ ] 4.5 앙상블 전략 실험 (선택적)
  - [ ] 4.6 Public/Private 과적합 방지 전략 수립

- [ ] 5.0 최종 제출 준비
  - [ ] 5.1 최종 프롬프트 템플릿 확정
  - [ ] 5.2 Test 데이터 처리 (test.csv → submission.csv)
  - [ ] 5.3 제출 파일 형식 검증
  - [ ] 5.4 최종 성능 문서화
  - [ ] 5.5 실험 과정 및 인사이트 정리
  - [ ] 5.6 GitHub 최종 백업 및 동기화

## 실험 우선순위

### Phase 1: 즉시 실행 (1-2시간)
- 베이스라인 성능 측정
- 데이터셋 분석 완료
- Few-shot 예시 실험

### Phase 2: 단기 개선 (2-4시간)
- 오류 유형별 프롬프트 최적화
- Chain-of-Thought 실험
- 성능 비교 분석

### Phase 3: 자동화 구축 (4-6시간)
- 배치 실험 시스템
- 결과 분석 자동화
- 최적 템플릿 선택

### Phase 4: 최종 최적화 (6-8시간)
- Multi-turn 전략 실험
- 앙상블 전략 검토
- 최종 제출 준비

## 성공 기준

- [ ] Recall 75% 이상 달성
- [ ] 최소 20개 이상 프롬프트 버전 실험
- [ ] 오류 유형별 최적 전략 도출
- [ ] 모든 실험 결과 재현 가능
- [ ] Public/Private 격차 5% 이내