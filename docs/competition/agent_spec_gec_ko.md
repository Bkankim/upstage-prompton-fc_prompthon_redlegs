# Korean GEC Competition — Agent Ops Spec (v1.0)
Date: 2025-10-23 11:52 KST
Owner: BK
Target Agents: Claude Code / Copilot / “Codex-like” code agents

---

## 0) TL;DR for the Agent
- **Goal**: Given Korean sentences, output minimally edited, grammatically correct sentences while **maximizing recall** (don’t miss true errors) and **avoiding semantic drift**.
- **Primary constraints**: Follow the competition docs you’re given (`overview_agents.md`, `datasetguide.md`, `evaluation.md`). Preserve meaning; do **not** rephrase style or tone unless it fixes a grammatical error. Prefer **few, surgical edits**.
- **Top strategy**: 3-stage pipeline — (A) detect & propose edits → (B) correct & validate → (C) rule-checklist & final polish — with **Self-Consistency** decoding and **Self-Refine/Reflexion**-style iterative feedback.
- **Hard stops**: No external web calls unless rules allow it. Stay within any API/token/call budgets specified by the competition docs.
- **Submission format**: Conform exactly to the competition’s I/O format (CSV/JSON/lines). Fail closed (skip-case) rather than emitting malformed output.

> References for reasoning strategies (Self-Consistency, Self-Refine, Reflexion) are listed at the bottom.

---

## 1) Inputs & Outputs
- **Input**: A text item (single sentence or short passage) in Korean.
- **Output**: The corrected text, **meaning-preserving** and **minimally edited**.
- **Batch I/O**: Follow the competition file schema (e.g., `id,text` → `id,corrected_text`). Keep columns and encodings identical to the guide. If a line cannot be corrected safely, return the original text.

> NOTE: You will receive the official docs alongside this spec. Read them first and cache: `overview_agents.md`, `datasetguide.md`, `evaluation.md`.

---

## 2) Optimization Target (Key Metric)
- Optimize for **Recall** under the task’s evaluation (often token-level recall via LCS approximations). That means: **catch as many actual errors as possible** without introducing hallucinated changes.
- **Trade-off policy**: Prefer a **small false positive** over a **missed true error** only when precision penalties are clearly smaller than recall penalties in the official metric. When uncertain, output the **original** (risk-averse).

---

## 3) Three-Expert Tree-of-Thought (ToT) Collaboration
Run three lightweight experts in sequence for each item. At each stage they share a single step of thinking; irrelevant paths are dropped.

1) **Expert A – Detector**: generate a concise list of suspected errors (categories + spans).  
2) **Expert B – Corrector**: propose minimal edits for each suspected error; keep meaning.  
3) **Expert C – Referee**: review A/B, remove over-edits, ensure style preservation & rules compliance.

**Update rule**: If any expert deviates from constraints (style rewrite, unsupported rule), **eliminate that path** and continue with the remaining experts.

---

## 4) Decoding & Iteration
- **Self-Consistency (SC)**: sample 3–7 candidate corrections with light randomness; choose the **most consistent** correction (majority/consensus on edits).  
- **Self-Refine loop (<= 2 iters)**: ask a brief *critic* to point out violations (overcorrection, rule breaks), then patch only those parts.  
- **Reflexion memo (optional)**: keep a short rolling memory of common mistakes for this dataset (e.g., ‘되/돼’, 의존 명사 띄어쓰기). Reuse as hints in later items.

---

## 5) Mandatory Rule-Checklist (Korean)
Apply this **after** model correction, before final emit. Only fix if mismatch is clear; otherwise keep original.

1) **‘되/돼’ 활용**
   - 동사 ‘되다’의 활용에서 ‘되어/돼, 되어서/돼서, 되어요/돼요’는 ‘돼/돼서/돼요’가 맞음. ‘되요, 되서’는 잘못.  
   - ‘안 돼’(동사 ‘되다’의 부정)는 **띄어씀**. 형용사 ‘안되다’(딱하다 등)는 붙여씀.  
2) **‘-ㄹ 수 있다’ 띄어쓰기**
   - ‘수’는 **의존 명사** → ‘할 수 있다/없다’는 **반드시 띄어씀**.  
3) **보조 용언 띄어쓰기(원칙 띄어씀, 일부 허용 붙임)**
   - ‘-아/어 보다, -아/어 보이다, -아/어 버리다, -아/어 놓다, -아/어 두다’ 등 → 원칙은 **띄어쓰기** (예: ‘읽어 보았다’). 일부 2음절 본용언 등은 붙임 허용(예: ‘나가버렸다’).  
4) **‘안/않’ 구분**
   - 통사적 부정은 **‘안 + 용언’ 띄어쓰기**(예: 안 가다), ‘안 되다’도 여기에 해당.  
   - 형용사 ‘안되다’는 **붙여씀**(딱하다, 불쌍하다).  
5) **외래어·고유명 표기**
   - 가능하면 국립국어원 외래어 표기를 따름. 경쟁 과제 범위 내에서만 제한적으로 정정.  
6) **최소 수정 원칙**
   - 의미/어조 보존, 불필요한 단어 치환 금지, 문체 균질 유지.

(공식 근거: 국립국어원 온라인가나다 및 한글 맞춤법—참고 문헌 하단 표기)

---

## 6) Prompts (drop-in)
Use these exactly (few-shot examples may be added from the training set where allowed).

### 6.1 Detector (Expert A)
```
You are Expert A (Detector). Task: Given a Korean sentence, list ONLY suspected errors as JSON.
Rules: be concise; don’t propose fixes; preserve meaning.

INPUT: "{text}"

OUTPUT JSON schema:
{{
  "suspected_errors": [
    {{"type": "<category>", "span": "<exact substring>", "rationale": "<why>", "severity": "high|med|low"}}
  ]
}}
```
### 6.2 Corrector (Expert B)
```
You are Expert B (Corrector). Given the original text and Expert A’s list, propose MINIMAL corrections.
Rules: keep meaning/style; only fix clear errors.

INPUT:
- ORIGINAL: "{text}"
- ERRORS_JSON: {errors_json}

OUTPUT JSON schema:
{{
  "corrections": [
    {{"before": "<span>", "after": "<replacement>", "reason": "<rule name>"}}
  ],
  "corrected_text": "<full corrected sentence>"
}}
```
### 6.3 Referee (Expert C)
```
You are Expert C (Referee). Review the corrected_text against the rules. Remove overcorrections, ensure formatting, and apply the Rule-Checklist.

INPUT:
- ORIGINAL: "{text}"
- CORRECTED: "{corrected_text}"
- CORRECTIONS: {corrections_json}

OUTPUT JSON schema:
{{
  "final_text": "<final>",
  "notes": ["kept minimal edits", "no semantic drift", "..."]
}}
```

### 6.4 Self-Refine Critic (max 2 passes)
```
You are a strict Korean grammar critic. Point out ONLY concrete violations (cite checklist item #).
Return a short patch list. If none, say "OK".
INPUT: "{candidate}"
OUTPUT (examples):
- "Checklist(1): '되요'→'돼요'"
- "Checklist(2): '할수있다'→'할 수 있다'"
- "OK"
```

---

## 7) Beginner-Friendly Reference Code

### 7.1 Token-level LCS Recall (eval helper)
```python
# -*- coding: utf-8 -*-
from typing import List, Tuple

def lcs_length(a: List[str], b: List[str]) -> int:
    """
    초보자 설명:
    - LCS(Longest Common Subsequence)는 두 시퀀스(여기서는 토큰 목록)에서
      순서는 유지하되 꼭 연속일 필요는 없는 '가장 긴 공통 부분열'의 길이를 의미합니다.
    - 아래 코드는 전형적인 동적 계획법(DP) 테이블을 사용해 LCS 길이를 구합니다.
    """
    n, m = len(a), len(b)
    dp = [[0]*(m+1) for _ in range(n+1)]
    for i in range(1, n+1):
        for j in range(1, m+1):
            if a[i-1] == b[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1  # 두 토큰이 같으면 대각선 값 + 1
            else:
                # 다르면 왼쪽/위쪽 값 중 더 큰 값을 선택
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    return dp[n][m]

def recall_by_lcs(pred: List[str], gold: List[str]) -> float:
    """
    - '재현율(Recall)'은 '정답 중에 내가 맞춘 비율'입니다.
    - 여기서는 LCS 길이를 정답(gold) 길이로 나누어 근사적으로 계산합니다.
    - 예: gold 토큰 10개 중 LCS가 8이면, recall ≈ 0.8 (80%)
    """
    if not gold:
        return 1.0
    return lcs_length(pred, gold) / len(gold)
```

### 7.2 Rule-Checklist Patcher (safe heuristics)
```python
import re

def apply_rule_checklist(text: str) -> str:
    """
    - 규칙을 무조건 적용하지 않고, '명백한' 잘못만 바꿉니다.
    - 과교정(over-correction)을 피하기 위해 보수적으로 설계합니다.
    """
    out = text

    # (1) '되/돼' 활용: 되요/되서 -> 돼요/돼서 (국립국어원 온라인가나다 근거)
    out = re.sub(r'(?<![가-힣])되요(?![가-힣])', '돼요', out)
    out = re.sub(r'(?<![가-힣])되서(?![가-힣])', '돼서', out)

    # (1) '안 돼' 띄어쓰기: 흔한 오탈자 '안돼' → 문맥상 동사 부정으로 추정 시 '안 돼'
    # 지나친 과교정을 막기 위해 '안돼서/안돼요' 같은 직후 어미 패턴을 우선 보정
    out = re.sub(r'안돼요', '안 돼요', out)
    out = re.sub(r'안돼서', '안 돼서', out)
    out = re.sub(r'안된다', '안 된다', out)  # 문장체 보정(보수적)

    # (2) '할 수 있다' 띄어쓰기: '수'는 의존 명사 → '할수있다' -> '할 수 있다'
    out = re.sub(r'([가-힣])수( ?)(있[다어요습니다])', r'\1 수 \3', out)

    # (3) 보조 용언: '해보다/해보았다' → 원칙 띄어쓰기 '해 보다/해 보았다'
    # 지나친 보정 방지: 자주 나오는 패턴만 적용
    out = re.sub(r'해보([았았었엿])', r'해 보\1', out)
    out = re.sub(r'해봐(요)?', r'해 봐\1', out)

    return out
```

### 7.3 Safe Inference Skeleton (A→B→C + SC + Refine)
```python
from dataclasses import dataclass
from typing import Dict, Any, List

@dataclass
class StepResult:
    name: str
    payload: Dict[str, Any]

def expert_A_detect(model, text: str) -> StepResult:
    """
    - Detector 역할: 오류 후보만 JSON으로 산출.
    - 'model'은 프롬프트를 받아 JSON을 반환하는 함수라고 가정합니다.
    """
    prompt = f"""You are Expert A (Detector)...
INPUT: "{{text}}"
OUTPUT JSON schema: {{ "suspected_errors": [{{"type":"","span":"","rationale":"","severity":""}}] }}"""
    resp = model(prompt)  # 초보자: 모델 호출은 함수처럼 가정
    return StepResult("A_detect", resp)

def expert_B_correct(model, text: str, errors_json: Dict[str,Any]) -> StepResult:
    prompt = f"""You are Expert B (Corrector)...
ORIGINAL: "{{text}}"
ERRORS_JSON: {errors_json}"""
    resp = model(prompt)
    return StepResult("B_correct", resp)

def expert_C_referee(model, original: str, corrected: str, corrections: Dict[str,Any]) -> StepResult:
    prompt = f"""You are Expert C (Referee)...
ORIGINAL: "{{original}}"
CORRECTED: "{{corrected}}"
CORRECTIONS: {corrections}"""
    resp = model(prompt)
    return StepResult("C_referee", resp)

def self_refine_critic(model, candidate: str) -> List[str]:
    prompt = f"""You are a strict Korean grammar critic...
INPUT: "{{candidate}}"""
    notes = model(prompt)  # 'OK' 또는 패치 지시 리스트
    return notes if isinstance(notes, list) else [notes]

def run_pipeline(model, text: str, sc_samples: int = 3, max_refine: int = 2) -> str:
    """
    - Self-Consistency: 같은 입력에 대해 약간의 온도(temperature)를 높여 sc_samples개 생성,
      다수결/일치도가 높은 후보를 선택.
    - Self-Refine: 최대 max_refine회, critic 지시대로 국소 수정.
    - 마지막에 Rule-Checklist 패처를 1회 적용.
    """
    candidates = []
    for _ in range(sc_samples):
        a = expert_A_detect(model, text)
        b = expert_B_correct(model, text, a.payload)
        c = expert_C_referee(model, text, b.payload.get("corrected_text",""), b.payload)
        candidates.append(c.payload.get("final_text", b.payload.get("corrected_text", text)) or text)

    # 간단한 일치도 기반 선택(동일 문자열이 가장 많은 것 선택)
    from collections import Counter
    chosen, _ = Counter(candidates).most_common(1)[0]

    # Self-Refine (최대 2회)
    current = chosen
    for _ in range(max_refine):
        notes = self_refine_critic(model, current)
        if notes and isinstance(notes, list) and notes[0].strip().upper() != "OK":
            # 아주 단순한 패치 적용(실전에서는 위치/문구를 더 안전하게 처리)
            for n in notes:
                if "→" in n:
                    before, after = [s.strip() for s in n.split("→", 1)]
                    current = current.replace(before, after)
        else:
            break

    # 규칙 체크리스트(보수적) 적용
    final_text = apply_rule_checklist(current)
    return final_text
```

---

## 8) Offline Validation Checklist
- File format & encoding strictly match the guide (headers, order, utf-8).
- No empty outputs; if uncertain → return the original sentence.
- Diff review: ensure **only necessary** edits (character-level diff length is short).
- Sanity test with a small gold set; track LCS-based recall and spot-check FP rate.
- Log common errors; feed into Reflexion memo (short hints list).

---

## 9) Known-Strong Heuristics for Korean GEC
- ‘되/돼’ 활용(돼요/돼서/돼) 정규화.
- 의존 명사 ‘수’ 띄어쓰기(할 수 있다/없다).
- 보조 용언 기본 띄어쓰기(해 보다/읽어 보았다/적어 둔다), 단 허용 붙임은 과교정 금지.
- ‘안/않’ 구분: 통사적 부정 띄어쓰기(안 + 용언), 형용사 ‘안되다’는 붙임.
- 과도한 어휘 치환 금지(문장 어조/경어체 유지).

---

## 10) Reproducibility & Logging
- Fix random seeds/temperatures for SC runs.
- Save A/B/C JSON, critic notes, and final diffs for N samples per batch.
- Keep a tiny “hints.md” updated from Reflexion memo (dataset-specific pitfalls).

---

## 11) References (grounding)
- 되/돼 활용 및 표기: 국립국어원 온라인가나다 ‘되요/돼요’(2023-09-12) & ‘되세요’(2025-04-30).
- ‘-ㄹ 수 있다’에서 ‘수’는 의존 명사: 국립국어원 온라인가나다(2024-11-12), 띄어쓰기 해설.
- 보조 용언 띄어쓰기: 국립국어원 온라인가나다 사례 모음.
- ‘안 돼/안되다’ 구분: 새국어소식 ‘한글 맞춤법의 이해’(국립국어원).
- Self-Consistency: Wang et al., ICLR 2023 (Google Research page/arXiv).
- Self-Refine: Madaan et al., 2023 (selfrefine.info / arXiv).
- Reflexion: Shinn et al., 2023 (arXiv/ICLR 2025 proceedings reference).

(Include the official competition docs alongside this spec.)
