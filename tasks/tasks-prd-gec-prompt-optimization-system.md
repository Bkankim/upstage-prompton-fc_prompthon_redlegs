## Relevant Files

### 핵심 소스 코드 (src/)
- `code/src/prompts/` - 프롬프트 템플릿 모듈 (핵심 수정 대상)
  - `baseline.py` - 베이스라인 프롬프트
  - `fewshot_v2.py` - Few-shot v2 프롬프트
  - `errortypes_v3.py` - Error Types v3 프롬프트
  - `registry.py` - 프롬프트 레지스트리 (자동 등록 및 조회)
- `code/src/generator.py` - 통합 문장 생성기 클래스
- `code/src/evaluator.py` - 평가 클래스
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
- `code/outputs/logs/comparison_*.json` - 프롬프트 비교 분석
- `code/outputs/submissions/train/` - Train 데이터 교정 결과
- `code/outputs/submissions/test/` - LB 제출 파일
- `code/outputs/analysis/` - 상세 분석 CSV

### 테스트 (tests/)
- `code/tests/test_prompts.py` - 프롬프트 모듈 테스트 (24개)
- `code/tests/test_generator.py` - 생성기 테스트 (17개)
- `code/tests/test_metrics.py` - 메트릭 테스트 (26개)
- `code/tests/test_evaluator.py` - 평가기 테스트 (18개)

### Notes

- **⚠️ 중요: 모든 Python 실행은 반드시 `uv run python` 명령 사용**
- 베이스라인 코드는 이미 `/code` 폴더에 준비되어 있음
- uv를 사용한 의존성 관리 (pyproject.toml)
- Python 3.12 사용 (.python-version)
- 실험은 베이스라인 성능 측정부터 시작하여 점진적으로 개선
- 모든 실험 결과는 JSON 형식으로 로깅
- 상세 uv 가이드: `/docs/UV_ENVIRONMENT_GUIDE.md`

## Tasks

- [x] 1.0 베이스라인 성능 측정 및 분석
  - [x] 1.1 환경 설정 및 의존성 설치 확인 (uv sync)
  - [x] 1.2 API 키 설정 확인 (.env 파일)
  - [x] 1.3 데이터 파일 배치 확인 (code/data/train_dataset.csv)
  - [x] 1.4 베이스라인 프롬프트로 교정 실행 (scripts/generate.py --prompt baseline)
  - [x] 1.5 베이스라인 Recall 점수 측정 (scripts/evaluate.py)
  - [x] 1.6 오류 유형별 분석 결과 검토 (analysis.csv)
  - [x] 1.7 베이스라인 성능 문서화 (logs/baseline_results.json)

- [ ] 2.0 프롬프트 개선 전략 실험 (2024-2025 최신 기법 적용)
  - [x] 2.1 Few-shot 예시 추가 버전 작성 (prompts_v2_fewshot.py)
  - [x] 2.2 오류 유형 명시 버전 작성 (prompts_v3_errortypes.py)
  - [ ] 2.3 **[즉시] Rule-Checklist 후처리 시스템** (utils/rule_checklist.py)
    - [ ] '되/돼' 활용 규칙 구현
    - [ ] '-ㄹ 수 있다' 띄어쓰기 규칙 구현
    - [ ] 보조 용언 띄어쓰기 규칙 구현
    - [ ] '안/않' 구분 규칙 구현
    - [ ] 기존 모든 프롬프트에 적용 및 재평가
  - [ ] 2.4 **[최우선] Contrastive Denoising with Noisy CoT (CD-CoT)** (prompts/cd_cot.py)
    - [ ] 잘못된 교정 예시와 올바른 교정 대비 프롬프트
    - [ ] 노이즈 제거 메커니즘 구현
    - [ ] 일관성 투표 시스템 구현
    - [ ] **예상 효과: +17.8% 정확도 향상 (2024년 검증)**
  - [ ] 2.5 **3-Expert Tree-of-Thought 시스템** (prompts/three_experts_tot.py)
    - [ ] Expert A (Detector) - 오류 탐지 전문가 구현
    - [ ] Expert B (Corrector) - 교정 전문가 구현
    - [ ] Expert C (Referee) - 검증 및 규칙 적용 전문가 구현
    - [ ] JSON 기반 Expert 간 통신 프로토콜 구현
    - [ ] 통합 파이프라인 구축
  - [ ] 2.6 **Self-Consistency 앙상블 디코딩** (utils/self_consistency.py)
    - [ ] 3개 샘플 생성 (temperature 0.1-0.3 조절)
    - [ ] 다수결/일치도 기반 선택 알고리즘
    - [ ] Expert C에만 적용 (API 제한 최적화)
  - [ ] 2.7 **Instance-Adaptive Prompting (IAP)** (prompts/instance_adaptive.py)
    - [ ] 오류 유형별 특화 프롬프트 자동 선택
    - [ ] 동적 프롬프트 조정 메커니즘
    - [ ] 각 인스턴스별 최적 전략 적용
  - [ ] 2.8 **Logic-of-Thought (LoT) Prompting** (prompts/logic_of_thought.py)
    - [ ] 문법 규칙을 논리식으로 표현
    - [ ] 명제 논리 기반 추론 체인 구성
    - [ ] **예상 효과: CoT 대비 +4.35%, ToT 대비 +8% (2024년 검증)**
  - [ ] 2.9 **TEXTGRAD (Textual Gradients)** (utils/textgrad.py)
    - [ ] 자연어 피드백을 gradient로 활용
    - [ ] 반복적 개선 메커니즘
    - [ ] Self-Refine과 통합 가능
  - [ ] 2.10 각 시스템별 성능 측정 및 비교
  - [ ] 2.11 최적 전략 조합 선택

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

## 실험 우선순위 (2024-2025 최신 기법 반영)

### Phase 1: 즉시 실행 (완료)
- ✅ 베이스라인 성능 측정 (Train 32.24%, LB 34.04%)
- ✅ 데이터셋 분석 완료 (20개 오류 유형)
- ✅ Few-shot 실험 (과적합 확인: Train 35.92% → LB 31.91%)

### Phase 2: 즉시 구현 (30분-1시간, 높은 ROI)
1. **Rule-Checklist 후처리** - 즉시 +2-3%p
   - 구현 난이도: ⭐ (매우 낮음)
   - 모든 프롬프트에 적용 가능

### Phase 3: 최우선 구현 (1-2시간, 최고 ROI)
2. **Contrastive Denoising (CD-CoT)** - **+10-15%p (2024년 +17.8% 검증)**
   - 구현 난이도: ⭐⭐⭐ (중간)
   - 가장 높은 성능 향상 잠재력

### Phase 4: 핵심 아키텍처 (2-4시간)
3. **3-Expert ToT 시스템** - +5-7%p
   - 구현 난이도: ⭐⭐⭐ (중간)
   - 체계적 접근

4. **Self-Consistency** - +3-4%p
   - 구현 난이도: ⭐⭐ (낮음)
   - Expert C에만 적용

### Phase 5: 추가 최적화 (4-6시간)
5. **Instance-Adaptive Prompting** - +2-3%p
6. **Logic-of-Thought** - CoT 대비 +4.35%
7. **TEXTGRAD** - 지속적 개선

### Phase 6: 통합 최적화 (6-8시간)
- **통합 파이프라인** (Rule → CD-CoT → ToT → SC)
- API 호출 최적화 (3회 제한 준수)
- 체크포인트 및 재시작 기능

## 성공 기준

### 단기 목표 (현실적, 오늘-내일)
- [ ] Recall 50% 이상 달성 (현재 34.04% → +16%p)
  - Rule-Checklist: 36-37%
  - CD-CoT 추가: 46-52%
- [ ] CD-CoT 구현 및 검증 완료
- [ ] Public/Private 격차 5% 이내

### 중기 목표 (도전적, 2-3일)
- [ ] Recall 55% 이상 달성
- [ ] 통합 파이프라인 완성 (Rule → CD-CoT → ToT → SC)
- [ ] 최소 5개 핵심 기법 실험 완료
- [ ] 모든 오류 유형에 균형 잡힌 성능

### 장기 목표 (이상적, 대회 종료 전)
- [ ] Recall 60-65% 달성
- [ ] CD-CoT + ToT + SC + Instance-Adaptive 통합
- [ ] 오류 유형별 최적 전략 도출
- [ ] 재현 가능한 실험 프레임워크

## 예상 성능 향상 로드맵 (2024-2025 최신 기법 적용)

| 전략 | 현재 | 예상 개선 | 목표 Recall | 검증 근거 |
|------|------|----------|------------|-----------|
| Baseline | 34.04% | - | 34.04% | LB 실측 |
| + Rule-Checklist | 34.04% | +2-3%p | 36-37% | 국립국어원 규칙 |
| + CD-CoT | 36-37% | +10-15%p | 46-52% | **2024년 +17.8% 검증** |
| + 3-Expert ToT | 46-52% | +5-7%p | 51-59% | ToT 74% vs CoT 9% |
| + Self-Consistency | 51-59% | +3-4%p | 54-63% | 다수결 안정성 |
| + Instance-Adaptive | 54-63% | +2-3%p | **56-66%** | 오류별 최적화 |

### 대안 경로 (API 제한 고려)

| 경로 A (CD-CoT 중심) | 경로 B (ToT 중심) | 경로 C (하이브리드) |
|---------------------|------------------|-------------------|
| Rule-Checklist (36%) | Rule-Checklist (36%) | Rule-Checklist (36%) |
| CD-CoT (46-52%) | 3-Expert ToT (41-44%) | CD-CoT + ToT 병합 (48-55%) |
| Self-Consistency (50-56%) | Self-Consistency (44-48%) | Instance-Adaptive (50-58%) |
| **목표: 50-56%** | **목표: 44-48%** | **목표: 50-58%** |

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

### 과적합 방지 원칙
1. Train 특화 규칙 지양
2. 일반 문법 원칙 중심
3. 모든 오류 유형 균등 처리
4. Test 데이터 절대 참조 금지