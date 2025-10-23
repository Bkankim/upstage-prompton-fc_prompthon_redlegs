# 전문가 조언 기반 개선 전략

**작성일**: 2025-10-23
**상태**: 실행 중
**목적**: 외부 전문가 조언을 기반으로 한 체계적 성능 개선 전략

---

## 1. 현황 진단

### 1.1 현재 성능
```
최고 기록:
- Public LB: 34.0426%
- Private LB: 13.4454%
- 파일: outputs/submissions/test/submission_baseline_test_clean.csv

개선 버전 (콜론 버그 수정):
- Train Recall: 33.88%
- Train Precision: 15.34%
- 상태: LB 미제출
```

### 1.2 발견된 문제
1. **콜론 처리 버그** (해결 완료)
   - 비율 표기 "7:3" → "3" 으로 잘림 (83% 텍스트 손실)
   - 8개 심각한 오류 발생
   - 해결: 3단계 검증 로직 구현

2. **Public/Private 격차** (미해결)
   - 약 20%p 차이 (34.04% vs 13.45%)
   - 원인: 데이터 분포 차이 추정
   - 대응: 교차검증 필요

3. **문법 규칙 효과 불명확** (미검증)
   - 41개 케이스에서 차이 발생
   - 규칙별 순효과 미측정
   - 유지 여부 근거 부족

---

## 2. 전문가 조언 상세

### 2.1 Q1: 후처리 전략 방향

#### 조언 내용
```yaml
1차 방어선: 프롬프트 형식 제어
  - System 메시지에 "한 문장만, 콜론 금지, 설명 금지" 명시
  - Few-shot 2-3개로 축소
  - "원문 → 교정" 대신 정답 문장만 예시

2차 방어선: 구조화 출력 (선택)
  - JSON 형태: {"output": "교정문"}
  - 리스크: 파싱 오류 시 Recall 급락
  - 조건: 20문장 A/B 실험 후 결정

3차 방어선: 후처리 최소화
  - 명확한 메타데이터 패턴만 제거
  - 60% 길이 유지 가드 추가
  - 과도한 손실 시 원문 반환
```

#### 타당성 검증
```
[✅ 매우 타당] 프롬프트 레벨 제어
  - 근거: 후처리는 한계가 명확 (콜론 버그 경험)
  - 우선순위: 최우선
  - 실행: 즉시 A/B 실험

[⚠️ 타당하나 신중] JSON 구조화
  - 장점: 메타데이터 완전 제거
  - 단점: 파싱 오류 리스크
  - 우선순위: 중간 (프롬프트 개선 후)

[✅ 매우 긴급] 60% 길이 가드
  - 근거: 83% 손실 재발 방지
  - 구현: 간단하고 즉시 효과
  - 우선순위: 최우선
```

#### 실행 계획
```python
# [즉시 실행] 60% 길이 가드 구현
def _apply_postprocessing_with_guard(self, original, corrected):
    """
    후처리 후 원문 대비 60% 길이 유지 검증
    """
    processed = self.process(corrected)

    # 가드: 60% 미만 손실 시 원문 반환
    if len(processed) < len(original) * 0.6:
        logger.warning(
            f"과도한 길이 손실 감지: "
            f"{len(original)}자 → {len(processed)}자 "
            f"({len(processed)/len(original)*100:.1f}%) - 원문 유지"
        )
        return original

    return processed

# [내일 실행] 프롬프트 형식 제약 A/B
system_v1 = "한국어 문법 교정 전문가입니다."

system_v2 = """한국어 문법 교정 전문가입니다.

출력 규칙:
1. 교정된 문장만 출력 (설명 금지)
2. 콜론(:), 줄바꿈 절대 금지
3. "원문:", "교정:" 라벨 금지

출력: [교정된 문장]"""

# 20문장 샘플로 비교 실험
```

---

### 2.2 Q2: Public/Private 격차 해석

#### 조언 내용
```yaml
가설 평가:
  - Overfitting: 가능성 낮음 (Few-shot 최소)
  - 데이터 분포 차이: 가능성 높음 (254개 Train으로 추정 어려움)
  - Recall 계산 방식: 가능성 중간 (주최측 문의 필요)

대응 전략:
  1. 5-fold 교차검증으로 분산 계량화
  2. 유형별 Recall 편차 분석
  3. Private 대비 취약 유형 파악
  4. 일반화 중심 프롬프트 개선
```

#### 타당성 검증
```
[✅ 매우 타당하고 실행 가능]
  - 근거: 20%p는 비정상 (일반적 5-10%p)
  - 254개 → 5-fold (각 50개) 충분
  - 긴급성: 최우선 (방향성 결정 필수)

[분석 목표]
  1. Train 평균 Recall ± 표준편차 계산
  2. Private 13.45%가 범위 내인지 확인
  3. 범위 밖이면 "데이터 분포 차이" 확정
  4. 유형별 성과 편차 분석
```

#### 실행 계획
```python
# [내일 실행] 5-fold 교차검증
from sklearn.model_selection import KFold

def cross_validate_recall():
    """
    Train 254개를 5-fold로 분할하여 분산 측정
    """
    train_df = pd.read_csv('data/train.csv')
    kf = KFold(n_splits=5, shuffle=True, random_state=42)

    fold_results = []
    for fold_idx, (train_idx, val_idx) in enumerate(kf.split(train_df)):
        val_fold = train_df.iloc[val_idx]

        # 현재 baseline 프롬프트로 교정
        corrections = []
        for _, row in val_fold.iterrows():
            corrected = baseline_generate(row['err_sentence'])
            corrections.append(corrected)

        # Recall/Precision 계산
        recall, precision, _, _ = calculate_metrics(
            val_fold['err_sentence'].tolist(),
            val_fold['cor_sentence'].tolist(),
            corrections
        )

        fold_results.append({
            'fold': fold_idx + 1,
            'recall': recall,
            'precision': precision,
            'samples': len(val_idx)
        })

    # 통계 분석
    recalls = [r['recall'] for r in fold_results]
    mean_recall = np.mean(recalls)
    std_recall = np.std(recalls)

    print(f"5-Fold 교차검증 결과:")
    print(f"  Mean Recall: {mean_recall:.2f}% ± {std_recall:.2f}%")
    print(f"  95% CI: [{mean_recall - 2*std_recall:.2f}%, {mean_recall + 2*std_recall:.2f}%]")
    print(f"\nPrivate LB 13.45% 분석:")

    if 13.45 < mean_recall - 2 * std_recall:
        print(f"  → 범위 밖! 데이터 분포 차이 의심")
    else:
        print(f"  → 범위 내. 정상 변동")

    return fold_results

# [내일 실행] 유형별 성과 분석
def analyze_error_type_performance():
    """
    오류 유형별 Recall/Precision 계산
    """
    train_df = pd.read_csv('data/train.csv')

    error_types = train_df['type'].unique()
    type_performance = {}

    for error_type in error_types:
        subset = train_df[train_df['type'] == error_type]

        # 교정 실행
        corrections = [baseline_generate(err) for err in subset['err_sentence']]

        # 성과 계산
        recall, precision, _, _ = calculate_metrics(
            subset['err_sentence'].tolist(),
            subset['cor_sentence'].tolist(),
            corrections
        )

        type_performance[error_type] = {
            'count': len(subset),
            'recall': recall,
            'precision': precision
        }

    # 결과 시각화
    df_perf = pd.DataFrame(type_performance).T
    df_perf = df_perf.sort_values('recall')

    print("오류 유형별 성과:")
    print(df_perf)

    # 취약 유형 식별
    weak_types = df_perf[df_perf['recall'] < mean_recall - std_recall]
    print(f"\n취약 유형 (평균 - 1σ 이하):")
    print(weak_types)

    return type_performance
```

**예상 결과:**
```
5-Fold 교차검증:
  Fold 1: Recall 35.2%, Precision 16.1% (51개)
  Fold 2: Recall 32.8%, Precision 14.9% (51개)
  Fold 3: Recall 34.1%, Precision 15.6% (51개)
  Fold 4: Recall 33.5%, Precision 15.2% (50개)
  Fold 5: Recall 31.9%, Precision 14.3% (51개)

  Mean: 33.5% ± 1.2%
  95% CI: [31.1%, 35.9%]

  Private 13.45% → 범위 밖! (데이터 분포 차이 확정)

유형별 성과:
  조사오류: Recall 38.5% (강점)
  띄어쓰기: Recall 35.2% (평균)
  맞춤법: Recall 32.1% (약점)
  비문: Recall 28.9% (약점)
  단순오탈자: Recall 40.1% (강점)
```

---

### 2.3 Q3: Multi-turn vs Single-turn

#### 조언 내용
```yaml
Multi-turn 설계:
  Turn 1: 오류 탐지 (JSON 배열)
  Turn 2: 교정 실행 (탐지 결과 기반)
  Turn 3: 검증 (선택)

장점:
  - False Negative 감소
  - 규칙 기반 후처리 의존도 감소

단점:
  - 토큰 사용 증가
  - API 호출 3회 소진

권장:
  - 단일 턴 안정화 후 시도
  - 30개 샘플 A/B 실험
```

#### 타당성 검증
```
[⚠️ 타당하나 우선순위 낮음]
  - 전문가도 "단일 턴 안정화 후" 명시
  - 리스크: 토큰 2000에서 탐지 JSON 낭비
  - 우선순위: 낮음 (프롬프트 개선 후)

[보류 사유]
  1. 현재 Single-turn으로 34.04% 달성
  2. 프롬프트 최적화로 개선 여지 먼저 확인
  3. 토큰 효율성 검증 필요
```

#### 실행 계획
```python
# [추후 검토] Multi-turn 프로토타입
# 조건: 프롬프트 형식 제약 A/B 완료 후

def multi_turn_correction(err_sentence):
    """
    3-turn 교정 프로세스
    """
    # Turn 1: 오류 탐지
    detect_prompt = f"""문장에서 문법 오류를 찾아 JSON 배열로 제시하세요.
형식: [{{"type": "조사", "position": 5, "original": "을", "reason": "목적격"}}, ...]

문장: {err_sentence}"""

    errors_json = call_llm(detect_prompt)
    errors = json.loads(errors_json)

    # Turn 2: 교정 실행
    correct_prompt = f"""다음 오류를 교정하세요.
원문: {err_sentence}
오류: {errors}

교정된 문장만 출력하세요."""

    correction = call_llm(correct_prompt)

    # Turn 3: 검증 (선택)
    verify_prompt = f"""교정이 올바른지 확인하세요.
원문: {err_sentence}
교정: {correction}

문제가 있으면 수정, 없으면 그대로 출력하세요."""

    final = call_llm(verify_prompt)

    return final

# 30개 샘플 A/B 실험
sample_30 = train_df.sample(30, random_state=42)

single_turn_results = [baseline_generate(err) for err in sample_30['err_sentence']]
multi_turn_results = [multi_turn_correction(err) for err in sample_30['err_sentence']]

# 성과 비교
recall_single, _, _, _ = calculate_metrics(
    sample_30['err_sentence'], sample_30['cor_sentence'], single_turn_results
)
recall_multi, _, _, _ = calculate_metrics(
    sample_30['err_sentence'], sample_30['cor_sentence'], multi_turn_results
)

print(f"Single-turn: {recall_single:.2f}%")
print(f"Multi-turn: {recall_multi:.2f}%")
print(f"개선: {recall_multi - recall_single:+.2f}%p")
```

**보류 이유:**
- 프롬프트 형식 제약으로 먼저 메타데이터 문제 해결
- 토큰 효율성 검증 전 전면 도입 리스크
- 현재 Single-turn 성능도 충분히 개선 가능

---

### 2.4 Q4: 문법 규칙의 역할

#### 조언 내용
```yaml
정량 검증:
  - version_comparison.csv 41건을 규칙별 분류
  - 각 규칙의 TP/FP/FN 기여도 계산
  - 순효과 = (TP 증가 - FP 증가) / 전체

판단 기준:
  - 순효과 > 0: 유지
  - 순효과 < 0: 제거 또는 조건 강화
  - 불확실: 프롬프트 힌트로 대체

추가 가드:
  - 규칙 적용 전후 길이 차이 15% 이상 시 롤백
  - 이미 올바른 형태는 skip
```

#### 타당성 검증
```
[✅ 매우 타당하고 즉시 실행 가능]
  - 데이터 이미 준비됨 (version_comparison.csv)
  - 긴급성: 문법 규칙 유지 근거 부족
  - 예상 시간: 1-2시간

[분석 목표]
  1. "되/돼" 규칙: TP/FP 계산
  2. "보조용언 띄어쓰기": TP/FP 계산
  3. "의존명사 띄어쓰기": TP/FP 계산
  4. 순효과 계산 후 유지/제거 결정
```

#### 실행 계획
```python
# [즉시 실행] 규칙별 순효과 분석
def analyze_grammar_rule_effects():
    """
    version_comparison.csv 기반 규칙별 효과 분석
    """
    comparison_df = pd.read_csv('outputs/version_comparison.csv')

    # 규칙 패턴 정의
    rules = {
        '되/돼': {
            'pattern': r'돼(?=야|지|도|서|요)',
            'description': '용언 + 어미 "되" → "돼"'
        },
        '보조용언_띄어쓰기': {
            'pattern': r'(\w+)(보다|보이다|싶다|하다|되다|지다)(?=\s|$)',
            'description': '보조 용언 띄어쓰기'
        },
        '의존명사_띄어쓰기': {
            'pattern': r'(\w+)(수|것|만큼|뿐|적|지)(?=\s|이|을|가|도)',
            'description': '의존 명사 띄어쓰기'
        }
    }

    rule_effects = {}

    for rule_name, rule_info in rules.items():
        tp_gain = 0  # 규칙으로 정답에 가까워진 경우
        fp_loss = 0  # 규칙으로 정답에서 멀어진 경우
        neutral = 0  # 판단 불가

        for idx, row in comparison_df.iterrows():
            old_cor = row['old_correction']  # 규칙 O
            new_cor = row['new_correction']  # 규칙 X
            ground_truth = row['cor_sentence']  # 정답

            # 규칙 적용 여부 확인
            if not re.search(rule_info['pattern'], old_cor):
                continue

            # 정답 대비 거리 계산 (Levenshtein)
            dist_old = edit_distance(old_cor, ground_truth)
            dist_new = edit_distance(new_cor, ground_truth)

            if dist_old < dist_new:
                tp_gain += 1  # 규칙이 정답에 가까워짐
            elif dist_old > dist_new:
                fp_loss += 1  # 규칙이 정답에서 멀어짐
            else:
                neutral += 1

        # 순효과 계산
        net_effect = tp_gain - fp_loss
        total_affected = tp_gain + fp_loss + neutral

        rule_effects[rule_name] = {
            'tp_gain': tp_gain,
            'fp_loss': fp_loss,
            'neutral': neutral,
            'net_effect': net_effect,
            'total_affected': total_affected,
            'effectiveness': net_effect / total_affected if total_affected > 0 else 0
        }

    # 결과 출력
    print("문법 규칙별 순효과 분석:")
    print("-" * 80)
    for rule_name, effects in rule_effects.items():
        print(f"\n{rule_name}:")
        print(f"  정답 접근 (TP): {effects['tp_gain']}건")
        print(f"  정답 이탈 (FP): {effects['fp_loss']}건")
        print(f"  영향 없음: {effects['neutral']}건")
        print(f"  순효과: {effects['net_effect']:+d}건")
        print(f"  효과성: {effects['effectiveness']*100:.1f}%")

        # 판단
        if effects['net_effect'] > 0:
            print(f"  → ✅ 유지 (긍정적 효과)")
        elif effects['net_effect'] < 0:
            print(f"  → ❌ 제거 고려 (부정적 효과)")
        else:
            print(f"  → ⚠️ 중립 (프롬프트 힌트로 대체 고려)")

    return rule_effects

# 실행 및 결과 저장
rule_effects = analyze_grammar_rule_effects()
pd.DataFrame(rule_effects).T.to_csv('outputs/analysis/grammar_rule_effects.csv')
```

**예상 결과:**
```
문법 규칙별 순효과 분석:
────────────────────────────────────────────────────────────────────────────────

되/돼:
  정답 접근 (TP): 5건
  정답 이탈 (FP): 1건
  영향 없음: 2건
  순효과: +4건
  효과성: 50.0%
  → ✅ 유지 (긍정적 효과)

보조용언_띄어쓰기:
  정답 접근 (TP): 8건
  정답 이탈 (FP): 3건
  영향 없음: 4건
  순효과: +5건
  효과성: 33.3%
  → ✅ 유지 (긍정적 효과)

의존명사_띄어쓰기:
  정답 접근 (TP): 2건
  정답 이탈 (FP): 6건
  영향 없음: 3건
  순효과: -4건
  효과성: -36.4%
  → ❌ 제거 고려 (부정적 효과)
```

---

## 3. 최종 실행 순서

### 우선순위 A: 즉시 실행 (오늘)

```yaml
1. 규칙별 순효과 분석:
   - 파일: code/analyze_grammar_rule_effects.py
   - 목적: 문법 규칙 유지/제거 결정
   - 예상 시간: 1-2시간
   - 출력: outputs/analysis/grammar_rule_effects.csv

2. 60% 길이 가드 구현:
   - 파일: code/src/postprocessors/rule_checklist.py
   - 함수: _apply_postprocessing_with_guard()
   - 목적: 과도한 텍스트 손실 방지
   - 테스트: test_length_guard.py

3. 개선 버전 LB 제출:
   - 파일: outputs/baseline_test.csv
   - 목적: 콜론 버그 수정 효과 검증
   - 예상: Public ~34%, Private ~13-14%
```

### 우선순위 B: 중기 실행 (내일)

```yaml
4. 5-fold 교차검증:
   - 파일: code/analyze_cross_validation.py
   - 목적: 성능 분산 측정, Private 격차 원인 규명
   - 출력: outputs/analysis/cross_validation_results.json

5. 유형별 성과 분석:
   - 파일: code/analyze_error_type_performance.py
   - 목적: 취약 오류 유형 식별
   - 출력: outputs/analysis/error_type_performance.csv

6. 프롬프트 형식 제약 A/B:
   - 샘플: 20개 (train.csv)
   - 비교: 기존 vs 형식 강화
   - 측정: 메타데이터 출현 빈도, Recall 변화
```

### 우선순위 C: 추후 검토 (모레 이후)

```yaml
7. JSON 형태 실험:
   - 조건: 프롬프트 A/B 완료 후
   - 샘플: 20개
   - 리스크: 파싱 오류 평가

8. Multi-turn 프로토타입:
   - 조건: 프롬프트 최적화 완료 후
   - 샘플: 30개
   - 측정: Recall 개선 vs 토큰 증가
```

---

## 4. 예상 결과 및 성공 지표

### 단기 목표 (오늘~내일)
```
1. 규칙 분석 완료:
   - 유지할 규칙: 2-3개 (순효과 > 0)
   - 제거할 규칙: 0-1개 (순효과 < 0)
   - 프롬프트 힌트: 1-2개 (중립)

2. 60% 가드 구현:
   - 테스트 통과율: 100% (5/5 케이스)
   - 과도한 손실 방지 확인

3. LB 제출 결과:
   - Public: 34.0% 이상 (기존 최고 유지)
   - Private: 13.5% 이상 (콜론 버그 수정 효과)
```

### 중기 목표 (내일~모레)
```
4. 교차검증 결과:
   - Mean Recall: 33.5% ± 1.2%
   - Private 13.45% → 범위 밖 확인
   - 데이터 분포 차이 확정

5. 유형별 분석:
   - 강점 유형: 조사오류, 단순오탈자
   - 약점 유형: 비문, 맞춤법
   - 일반화 전략 수립

6. 프롬프트 A/B:
   - 메타데이터 출현: 50% 감소
   - Recall 유지 또는 개선
```

### 장기 목표 (일주일 내)
```
7. 통합 개선 버전:
   - Public LB: 35-36% (목표)
   - Private LB: 14-15% (목표)
   - 격차 축소: 20%p → 15%p 이하

8. 안정적 파이프라인:
   - 메타데이터 출현: <5%
   - 과도한 손실: 0건
   - 문법 규칙: 근거 기반 유지
```

---

## 5. 리스크 및 대응

### 리스크 1: 규칙 제거로 성능 하락
```
발생 조건:
  - 규칙별 순효과가 잘못 계산됨
  - 일부 긍정적 규칙을 제거함

대응:
  - A/B 실험으로 재검증
  - 규칙 제거 전후 Train Recall 비교
  - 하락 시 즉시 복원
```

### 리스크 2: 프롬프트 제약이 과도함
```
발생 조건:
  - 형식 제약이 너무 엄격해 창의성 저하
  - Recall 오히려 하락

대응:
  - 20개 샘플 A/B 먼저 실행
  - 하락 확인 시 제약 완화
  - 단계적 적용 (System만 → User 추가)
```

### 리스크 3: 교차검증 결과 해석 오류
```
발생 조건:
  - 분산이 너무 커서 결론 불가
  - Private 격차 원인을 잘못 판단

대응:
  - 주최측에 채점 방식 문의
  - Public/Private 데이터 샘플 요청
  - 보수적 전략 (일반화 최우선)
```

---

## 6. 참고 문서

- `/Competition/upstage-prompton-fc_prompthon_redlegs/outputs/version_comparison.csv` - 41건 차이 분석
- `/Competition/upstage-prompton-fc_prompthon_redlegs/outputs/logs/EXPERIMENT_LOG_SUMMARY.md` - 실험 이력
- `/Competition/upstage-prompton-fc_prompthon_redlegs/docs/advanced/EXPERIMENT_LESSONS.md` - 실험 교훈
- `/Competition/upstage-prompton-fc_prompthon_redlegs/code/analyze_colon_patterns.py` - 콜론 버그 분석
- `/Competition/upstage-prompton-fc_prompthon_redlegs/code/compare_versions.py` - 버전 비교 도구

---

## 7. 체크리스트

### 오늘 (2025-10-23)
- [ ] 규칙별 순효과 분석 완료
- [ ] 60% 길이 가드 구현 및 테스트
- [ ] 개선 버전 LB 제출

### 내일 (2025-10-24)
- [ ] 5-fold 교차검증 실행
- [ ] 유형별 성과 분석 완료
- [ ] 프롬프트 형식 제약 A/B 실험

### 모레 (2025-10-25)
- [ ] 교차검증 결과 기반 전략 수립
- [ ] 프롬프트 최적화 버전 전체 실험
- [ ] 규칙 검증 결과 반영

### 추후 검토
- [ ] JSON 형태 소규모 실험
- [ ] Multi-turn 프로토타입 검증
- [ ] 통합 개선 버전 LB 제출

---

**마지막 업데이트**: 2025-10-23
**다음 리뷰**: 2025-10-24 (LB 제출 결과 확인 후)
