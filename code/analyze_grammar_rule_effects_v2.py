"""
문법 규칙별 순효과 분석 스크립트 v2 (단순화된 로직)

1. no_rules 버전에 규칙을 직접 적용하여 simulated 버전 생성
2. simulated vs with_rules 비교하여 규칙이 적용된 케이스만 식별
3. 각 케이스에 대해 정답과의 편집 거리 계산
4. TP/FP 판정 및 순효과 계산
"""

import pandas as pd
import re
from pathlib import Path
import difflib


def apply_grammar_rules(text: str) -> tuple:
    """
    텍스트에 문법 규칙을 적용하고 어떤 규칙이 적용되었는지 반환

    Returns:
        (적용된 텍스트, 적용된 규칙 리스트)
    """
    # 규칙 정의
    rules = {
        "되/돼 활용": [
            (r'(?<![가-힣])되요(?![가-힣])', '돼요'),
            (r'(?<![가-힣])되서(?![가-힣])', '돼서'),
            (r'되여요', '돼요'),
            (r'되여서', '돼서'),
        ],
        "안 돼 띄어쓰기": [
            (r'안돼요', '안 돼요'),
            (r'안돼서', '안 돼서'),
            (r'안된다(?![가-힣])', '안 된다'),
            (r'안돼(?![가-힣])', '안 돼'),
        ],
        "수 있다 띄어쓰기": [
            (r'([가-힣])수있다', r'\1 수 있다'),
            (r'([가-힣])수있어', r'\1 수 있어'),
            (r'([가-힣])수있어요', r'\1 수 있어요'),
            (r'([가-힣])수있습니다', r'\1 수 있습니다'),
            (r'([가-힣])수없다', r'\1 수 없다'),
            (r'([가-힣])수없어', r'\1 수 없어'),
            (r'([가-힣])수없어요', r'\1 수 없어요'),
            (r'([가-힣])수없습니다', r'\1 수 없습니다'),
        ],
        "보조용언 띄어쓰기": [
            (r'해보다(?![가-힣])', '해 보다'),
            (r'해보았', '해 보았'),
            (r'해보았다', '해 보았다'),
            (r'해보았어', '해 보았어'),
            (r'해봤', '해 봤'),
            (r'해봤다', '해 봤다'),
            (r'해봤어', '해 봤어'),
            (r'해봐요', '해 봐요'),
            (r'해봐(?![가-힣])', '해 봐'),
            (r'해보자', '해 보자'),
        ]
    }

    original = text
    applied_rules = []

    for rule_name, patterns in rules.items():
        before = text
        for pattern, replacement in patterns:
            text = re.sub(pattern, replacement, text)
        if text != before:
            applied_rules.append(rule_name)

    return text, applied_rules


def calculate_edit_distance(text1: str, text2: str) -> int:
    """편집 거리 계산"""
    matcher = difflib.SequenceMatcher(None, text1, text2)
    matches = sum(block.size for block in matcher.get_matching_blocks())
    total_len = max(len(text1), len(text2))
    return total_len - matches


def main():
    """메인 실행"""
    code_dir = Path(__file__).parent

    # 파일 로드
    no_rules_df = pd.read_csv(code_dir / "outputs" / "submissions" / "train" / "submission_baseline_no_rules.csv")
    with_rules_df = pd.read_csv(code_dir / "outputs" / "submissions" / "train" / "submission_baseline.csv")
    train_df = pd.read_csv(code_dir / "data" / "train.csv")

    # 정답 매핑
    id_to_answer = dict(zip(train_df['err_sentence'], train_df['cor_sentence']))

    print("\n" + "=" * 80)
    print("문법 규칙별 순효과 분석 시작 (v2 - 단순화된 로직)")
    print("=" * 80)
    print(f"\n규칙 OFF: {len(no_rules_df)}건")
    print(f"규칙 ON: {len(with_rules_df)}건")
    print(f"Train: {len(train_df)}건")

    # 규칙별 통계
    rule_stats = {
        "되/돼 활용": {'TP': 0, 'FP': 0, 'NC': 0, 'cases': []},
        "안 돼 띄어쓰기": {'TP': 0, 'FP': 0, 'NC': 0, 'cases': []},
        "수 있다 띄어쓰기": {'TP': 0, 'FP': 0, 'NC': 0, 'cases': []},
        "보조용언 띄어쓰기": {'TP': 0, 'FP': 0, 'NC': 0, 'cases': []}
    }

    print("\n분석 시작...")
    print("=" * 80)

    for idx in range(len(no_rules_df)):
        err_sentence = no_rules_df.loc[idx, 'err_sentence']
        no_rules_cor = str(no_rules_df.loc[idx, 'cor_sentence'])
        with_rules_cor = str(with_rules_df.loc[idx, 'cor_sentence'])

        # 정답 가져오기
        answer = id_to_answer.get(err_sentence)
        if answer is None:
            continue

        # no_rules 버전에 규칙 적용
        simulated_cor, applied_rules = apply_grammar_rules(no_rules_cor)

        # 규칙이 적용됐는지 확인
        if not applied_rules:
            continue  # 규칙이 적용 안 된 케이스는 스킵

        # 편집 거리 계산
        no_rules_dist = calculate_edit_distance(no_rules_cor, answer)
        simulated_dist = calculate_edit_distance(simulated_cor, answer)

        # 효과 판정
        if simulated_dist < no_rules_dist:
            effect = 'TP'  # 규칙이 정답에 가까워짐
        elif simulated_dist > no_rules_dist:
            effect = 'FP'  # 규칙이 정답에서 멀어짐
        else:
            effect = 'NC'  # 변화 없음

        # 각 규칙별 집계
        for rule_name in applied_rules:
            rule_stats[rule_name][effect] += 1
            rule_stats[rule_name]['cases'].append({
                'idx': idx,
                'err': err_sentence[:80],
                'no_rules': no_rules_cor[:80],
                'simulated': simulated_cor[:80],
                'answer': answer[:80],
                'no_rules_dist': no_rules_dist,
                'simulated_dist': simulated_dist,
                'effect': effect
            })

        # 진행 상황
        if (idx + 1) % 50 == 0:
            print(f"진행: {idx + 1}/{len(no_rules_df)}")

    print("=" * 80)

    # 결과 집계
    results = []
    for rule_name, stats in rule_stats.items():
        tp = stats['TP']
        fp = stats['FP']
        nc = stats['NC']
        total_affected = tp + fp + nc

        # 순효과 및 효과성 계산
        net_effect = tp - fp
        effectiveness = (net_effect / total_affected * 100) if total_affected > 0 else 0

        # 판단 기준 적용
        if total_affected < 5:
            decision = "⚠️ 데이터 부족"
            reason = f"샘플 {total_affected}건 < 최소 5건"
        elif net_effect >= 2 and effectiveness >= 30:
            decision = "✅ 유지"
            reason = f"순효과 {net_effect:+d}, 효과성 {effectiveness:.1f}%"
        elif net_effect <= -1:
            decision = "❌ 제거"
            reason = f"순효과 {net_effect:+d} (부정적)"
        else:
            decision = "⚠️ 프롬프트 힌트 검토"
            reason = f"순효과 {net_effect:+d}, 효과성 {effectiveness:.1f}%"

        results.append({
            '규칙': rule_name,
            'TP': tp,
            'FP': fp,
            'NC': nc,
            '영향_케이스': total_affected,
            '순효과': net_effect,
            '효과성(%)': round(effectiveness, 1),
            '판단': decision,
            '사유': reason
        })

    result_df = pd.DataFrame(results)

    # 결과 출력
    print("\n[규칙별 순효과 분석 결과]")
    print("=" * 80)
    print(result_df.to_string(index=False))
    print("=" * 80)

    # 결과 저장
    output_dir = code_dir / "outputs" / "analysis"
    output_dir.mkdir(parents=True, exist_ok=True)

    result_path = output_dir / "grammar_rule_effects.csv"
    result_df.to_csv(result_path, index=False, encoding='utf-8-sig')
    print(f"\n✅ 분석 결과 저장: {result_path}")

    # 상세 케이스 저장
    print("\n[상세 케이스 저장]")
    for rule_name, stats in rule_stats.items():
        if stats['cases']:
            cases_df = pd.DataFrame(stats['cases'])
            safe_name = rule_name.replace('/', '_').replace(' ', '_')
            output_path = output_dir / f"rule_cases_{safe_name}.csv"
            cases_df.to_csv(output_path, index=False, encoding='utf-8-sig')
            print(f"저장: {output_path} ({len(cases_df)}건)")

    print("\n" + "=" * 80)
    print("분석 완료!")
    print("=" * 80)


if __name__ == "__main__":
    main()
