---
title: "GEC Promptathon - Agent Guide"
version: "1.2"
last_updated: "2025-10-22"
purpose: "에이전트(Claude Code 등)가 대회 조력자로 활동할 때 참조하는 실행 가이드"
---

# Mission
**역할:** 한국어 문장 교정 프롬프트 설계·실험·평가·제출을 자동화하는 조력자  
**목표:** 프롬프팅만으로 Recall 최대화 + 재현 가능한 템플릿/스크립트 산출  
**의의:** 프롬프트 엔지니어링 실전 경험 + LLM 활용법 학습 + 실제 비즈니스 문제 해결

---

# Competition Overview

## 기본 정보
- **과제:** 프롬프트만으로 한국어 맞춤법/띄어쓰기/문장부호 교정
- **모델:** Upstage Solar Pro 2
- **평가 지표:** Recall (재현율)
- **팀 구성:** 1-3인 (개인 가능)

## 핵심 제약사항
- **세션 토큰:** 2000 이하
- **API 호출:** 케이스당 최대 3회
- **외부 데이터:** 사용 금지
- **RAG:** 제공 데이터셋 내부만 허용
- **Multi-turn:** 허용 (토큰 제한 내)
- **일일 제출:** 팀당 20회 (KST 자정 리셋)

---

# Dataset

## 구조
```
data/
├── train_dataset.csv    (254 rows)
├── test.csv            (109 rows)
└── sample_submission.csv
```

## 컬럼 정보

**Train 전용:**
- `type`: 오류 유형 (조사오류, 맞춤법, 비문, 단순오탈자 등)
- `original_target_part`: 원문 중 오류 부분
- `golden_target_part`: 교정되어야 할 부분
- `corrected`: 교정된 정답 문장

**공통:**
- `err_sentence`: 오류가 있는 원문 (`original` in train)

---

# Evaluation

## Primary Metric: Recall

$$Recall = \frac{TP}{TP + FP + FN} \times 100$$

| 약어 | 정의 |
|------|------|
| TP | True Positive - 올바르게 교정 |
| FP | False Positive - 잘못 교정 |
| FN | False Negative - 교정 놓침 |
| FR | False Redundant - 불필요한 수정 |

**참고:** Precision도 계산되나 순위는 Recall로만 결정

## 평가 방법
1. **토큰화:** 공백 기준 분할
2. **비교:** LCS(최장 공통 부분 수열) 알고리즘으로 정답 vs 예측 비교
3. **판정:** 토큰 단위로 TP/FP/FN/FR 계산

## Leaderboard
- **Public:** 40% (대회 중 실시간)
- **Private:** 60% (종료 후 최종 순위)

---

# Prompt Template Submission Format

## 구글폼 제출 양식 (JSON)

최종 제출 시 아래 JSON 형식을 구글폼에 입력해야 합니다.
```json
{
    "template_name": "PromptTemplate_YourName_v1",
    "description": "프롬프트 템플릿에 대한 간단한 설명",
    "prompt": {
        "system": "시스템 프롬프트 내용",
        "user_turns": [
            {
                "user": "1차 사용자 프롬프트"
            },
            {
                "user": "2차 사용자 프롬프트 (선택)"
            }
        ]
    },
    "multi_turn": false,
    "function_calling": false,
    "function_details": {
        "function_name": "함수명 (function_calling 사용 시)",
        "description": "함수 설명"
    },
    "parameters": {
        "temperature": 0.1,
        "max_tokens": 2000
    },
    "api_call_strategy": {
        "calls_per_case": 1
    }
}
```

## 필드 설명

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `template_name` | string | ✅ | 템플릿 고유 이름 |
| `description` | string | ✅ | 템플릿 설명 |
| `prompt.system` | string | ✅ | 시스템 프롬프트 |
| `prompt.user_turns` | array | ✅ | 사용자 프롬프트 턴 (1개 이상) |
| `multi_turn` | boolean | ✅ | 다단계 대화 사용 여부 |
| `function_calling` | boolean | ✅ | 함수 호출 사용 여부 |
| `function_details` | object | ⚪ | function_calling=true 시 필수 |
| `parameters.temperature` | float | ✅ | 0.0-1.0 (낮을수록 일관성↑) |
| `parameters.max_tokens` | integer | ✅ | 최대 출력 토큰 |
| `api_call_strategy.calls_per_case` | integer | ✅ | 케이스당 API 호출 횟수 (1-3) |

## 예시 템플릿

### 기본 Single-turn
```json
{
    "template_name": "Basic_GEC_v1",
    "description": "기본 문법 교정 템플릿",
    "prompt": {
        "system": "당신은 한국어 맞춤법 교정 전문가입니다. 띄어쓰기, 맞춤법, 조사 사용, 문장 부호 등 모든 문법적 오류를 교정합니다. 반드시 교정된 문장만 출력하세요.",
        "user_turns": [
            {
                "user": "다음 문장을 교정하세요: {err_sentence}"
            }
        ]
    },
    "multi_turn": false,
    "function_calling": false,
    "parameters": {
        "temperature": 0.1,
        "max_tokens": 2000
    },
    "api_call_strategy": {
        "calls_per_case": 1
    }
}
```

### Multi-turn with Verification
```json
{
    "template_name": "TwoStep_Verification_v1",
    "description": "2단계 검증 템플릿",
    "prompt": {
        "system": "당신은 한국어 맞춤법 교정 전문가입니다.",
        "user_turns": [
            {
                "user": "1차: 다음 문장의 오류를 찾으세요: {err_sentence}"
            },
            {
                "user": "2차: 발견한 오류를 교정하고 최종 문장만 출력하세요."
            }
        ]
    },
    "multi_turn": true,
    "function_calling": false,
    "parameters": {
        "temperature": 0.1,
        "max_tokens": 2000
    },
    "api_call_strategy": {
        "calls_per_case": 2
    }
}
```

---

# Template Evaluation Criteria

제출된 프롬프트 템플릿은 다음 5가지 기준으로 평가됩니다:

## 1. 실행 가능성 및 실용성
- 실제 작동 가능한가?
- 재현 가능한가?
- 제약 조건(토큰, API 호출 등) 준수했는가?

## 2. 최적화 및 효율성
- 토큰을 효율적으로 사용하는가?
- 불필요한 API 호출이 없는가?
- 처리 속도가 적절한가?

## 3. 창의성 및 독창성
- 새로운 접근 방식을 시도했는가?
- 차별화된 전략이 있는가?
- 혁신적인 아이디어가 포함되었는가?

## 4. 명료성 및 논리성
- 프롬프트가 명확한가?
- 지시사항이 논리적인가?
- 이해하기 쉬운가?

## 5. 기술 적합성 및 난이도
- 문제에 적합한 기술을 사용했는가?
- 구현 난이도가 적절한가?
- 발표 품질은 어떠한가?

---

# Competition Workflow

## 전체 프로세스
```
1. 다양한 프롬프트 템플릿 실험
   ├─ 기본 템플릿 (Single-turn)
   ├─ Multi-turn 템플릿
   ├─ Few-shot 템플릿
   └─ Chain-of-Thought 템플릿
   
2. 최적의 프롬프트 템플릿 선택
   ├─ Train 데이터로 평가
   ├─ Recall 점수 비교
   └─ 최고 성능 템플릿 선택
   
3. 테스트 데이터에 대한 예측 수행
   ├─ 선택된 템플릿으로 test.csv 처리
   └─ 교정 결과 생성
   
4. submission.csv 형식으로 제출
   ├─ id, err_sentence, cor_sentence 포함
   ├─ UTF-8 인코딩 확인
   └─ 리더보드 제출 (하루 최대 20회)
```

---

# Prompt Template Structure

## System Prompt (기본 템플릿)
```
당신은 한국어 문장 교정 전문가입니다.
맞춤법, 띄어쓰기, 문장부호를 교정하되 의미를 왜곡하거나 불필요한 재작성은 금지합니다.
원문의 어조를 유지하고, 변경이 없으면 원문 그대로 반환하세요.
```

## User Prompt (기본 템플릿)
```
다음 문장을 교정하세요:
{err_sentence}
```

## Multi-turn 옵션
```
# 1차 턴: 오류 탐지
다음 문장에서 맞춤법, 띄어쓰기, 문장부호 오류를 찾으세요:
{err_sentence}

# 2차 턴: 교정 실행
발견한 오류를 교정하고 교정된 문장만 출력하세요.
```

---

# Experiment Workflow

## 기본 흐름
```
1. 프롬프트 템플릿 설계
   ↓
2. 파라미터 그리드 설정 (temperature, top_p 등)
   ↓
3. Train 데이터로 평가
   ↓
4. Recall 최고 템플릿 선택
   ↓
5. Test 데이터 예측 및 제출
```

## 핵심 코드 (개념)
```python
def eval_recall(tp, fp, fn):
    """Recall 계산"""
    return (tp / (tp + fp + fn) * 100) if (tp + fp + fn) > 0 else 0.0

def run_experiment(template, dataset):
    """한 템플릿 평가"""
    tp = fp = fn = 0
    for row in dataset:
        pred = call_model(template, row['err_sentence'])
        result = compare(pred, row['corrected'])  # TP/FP/FN 판정
        tp += (result == 'TP')
        fp += (result == 'FP')
        fn += (result == 'FN')
    return eval_recall(tp, fp, fn)
```

---

# Experiment Log

## 필수 기록 항목
- `run_id`: 실험 고유 ID
- `template_id`: 템플릿 식별자
- `template_json`: 전체 템플릿 JSON
- `temperature`, `top_p`, `max_tokens`: 파라미터
- `multi_turn`, `function_calling`: 옵션
- `calls_per_case`: API 호출 횟수
- `tp`, `fp`, `fn`, `fr`: 평가 결과
- `recall`, `precision`: 점수

## 저장 형식
```python
# logs/experiment_YYYYMMDD_HHMMSS.json
{
  "run_id": "exp_001",
  "template_name": "Basic_GEC_v1",
  "template_json": {...},  # 전체 JSON 저장
  "params": {
    "temperature": 0.1, 
    "max_tokens": 2000,
    "calls_per_case": 1
  },
  "results": {
    "tp": 200, 
    "fp": 30, 
    "fn": 24, 
    "fr": 15,
    "recall": 78.74,
    "precision": 81.63
  }
}
```

---

# Deliverables

## 필수 제출물

1. **리더보드 제출** (최대 2개)
   - submission.csv (id, err_sentence, cor_sentence)

2. **구글폼 제출** (템플릿 JSON)
   - 최종 선택한 프롬프트 템플릿
   - 위의 JSON 형식 준수

3. **프로젝트 페이지**
   - GitHub 저장소 또는 문서
   - README.md 포함
   - 재현 스크립트 포함

4. **발표 자료** (PPT)
   - 문제 정의
   - 접근 방법
   - 실험 결과
   - 핵심 인사이트
   - 개선 방안

---

# Action Checklist

## 실험 단계
- [ ] 세션 토큰 ≤ 2000 확인
- [ ] 케이스당 API 호출 ≤ 3 확인
- [ ] 기본 템플릿 작성 (system + user)
- [ ] 템플릿 변형 실험 (Multi-turn, Few-shot, CoT)
- [ ] 파라미터 그리드 테스트 (temperature: 0.1/0.2/0.3)
- [ ] Recall 계산 및 로그 저장
- [ ] 최고 성능 템플릿 선택

## 제출 단계
- [ ] Test 데이터 예측 (109개)
- [ ] submission.csv 생성 및 검증
- [ ] 구글폼에 템플릿 JSON 제출
- [ ] 리더보드 제출 (하루 20회 제한 확인)

## 문서화
- [ ] README.md 작성
- [ ] 실험 로그 정리
- [ ] 재현 스크립트 준비
- [ ] 발표 자료 작성 (5가지 평가 기준 고려)

---

# Key Insights

## Recall 최적화 전략

### 1. False Negative 최소화가 핵심
- 놓치는 것(FN)이 가장 큰 패널티
- 의심스러우면 교정하는 편이 유리
- 과도한 보수성은 Recall 하락

### 2. 다단계 검증 활용
- Multi-turn으로 2-3단계 검증
- 1차: 오류 탐지
- 2차: 교정 실행
- 3차: 최종 검토 (선택)

### 3. 오류 유형별 전략
Train 데이터의 `type` 활용:
- 조사오류: "을/를, 이/가" 패턴
- 맞춤법: 자주 틀리는 단어 리스트
- 띄어쓰기: 복합명사 규칙
- 단순오탈자: 비슷한 글자 확인

### 4. Few-shot Learning
```
예시 1:
원문: 감자기 일어났다
교정: 갑자기 일어났다

예시 2:
원문: 그는 책을 읽고있다
교정: 그는 책을 읽고 있다

이제 다음 문장을 교정하세요:
{err_sentence}
```

## 주의사항
- **Public 과적합 경계** (40%만 반영)
- **세션 토큰 제한** (2000) 엄수
- **외부 데이터 절대 금지**
- **API 호출 최적화** (비용 고려)
- **일일 제출 제한** (20회) 관리

---

# Template Examples

## Template 1: Basic Single-turn
```json
{
    "template_name": "Basic_v1",
    "description": "단순 교정 템플릿",
    "prompt": {
        "system": "한국어 맞춤법 전문가로서 띄어쓰기, 맞춤법, 문장부호를 교정합니다. 교정된 문장만 출력하세요.",
        "user_turns": [
            {"user": "교정: {err_sentence}"}
        ]
    },
    "multi_turn": false,
    "function_calling": false,
    "parameters": {"temperature": 0.1, "max_tokens": 2000},
    "api_call_strategy": {"calls_per_case": 1}
}
```

## Template 2: Chain-of-Thought
```json
{
    "template_name": "CoT_v1",
    "description": "단계별 추론 템플릿",
    "prompt": {
        "system": "한국어 교정 전문가입니다. 단계별로 생각하세요:\n1. 오류 유형 파악\n2. 교정 방법 결정\n3. 최종 문장 출력",
        "user_turns": [
            {"user": "다음 문장을 단계별로 분석하고 교정하세요:\n{err_sentence}\n\n최종 교정 결과만 출력하세요."}
        ]
    },
    "multi_turn": false,
    "function_calling": false,
    "parameters": {"temperature": 0.2, "max_tokens": 2000},
    "api_call_strategy": {"calls_per_case": 1}
}
```

## Template 3: Two-Step Verification
```json
{
    "template_name": "TwoStep_v1",
    "description": "2단계 검증 템플릿",
    "prompt": {
        "system": "한국어 교정 전문가입니다.",
        "user_turns": [
            {"user": "1단계: 오류 찾기\n{err_sentence}"},
            {"user": "2단계: 교정 실행 (교정된 문장만 출력)"}
        ]
    },
    "multi_turn": true,
    "function_calling": false,
    "parameters": {"temperature": 0.1, "max_tokens": 2000},
    "api_call_strategy": {"calls_per_case": 2}
}
```

---

# References
- 대회 페이지: https://stages.ai/en/competitions/403
- Solar Prompt 강좌: https://edu.upstage.ai/course/prompt-design
- 토큰 계산기: https://console.upstage.ai/docs/guides/counting-tokens
- LCS 알고리즘: https://ko.wikipedia.org/wiki/최장_공통_부분_수열
- Precision/Recall: https://en.wikipedia.org/wiki/Precision_and_recall

---

**Version:** 1.2  
**Last Updated:** 2025-10-22  
**Target:** AI Agents (Claude Code, Codex 등)