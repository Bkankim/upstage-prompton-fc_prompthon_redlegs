"""
문법 규칙별 순효과 분석 스크립트

version_comparison.csv 41건을 분석하여 각 문법 규칙의 효과를 측정한다.
- TP: edit_distance(규칙_적용, 정답) < edit_distance(규칙_미적용, 정답)
- FP: edit_distance(규칙_적용, 정답) > edit_distance(규칙_미적용, 정답)
- 순효과: TP 건수 - FP 건수
- 효과성: 순효과 / 영향받은 케이스 수 × 100
"""

import pandas as pd
import re
from pathlib import Path
from typing import Dict, List, Tuple
import difflib


# 문법 규칙 정의 (rule_checklist.py와 동일)
GRAMMAR_RULES = {
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


def apply_grammar_rules(text: str) -> str:
    """
    텍스트에 문법 규칙 적용

    Args:
        text: 입력 텍스트

    Returns:
        규칙이 적용된 텍스트
    """
    for rule_name, patterns in GRAMMAR_RULES.items():
        for pattern, replacement in patterns:
            text = re.sub(pattern, replacement, text)
    return text


def detect_applied_rules(old_text: str, new_text: str) -> List[str]:
    """
    old_text와 new_text를 비교하여 적용된 규칙을 감지

    Args:
        old_text: 규칙 미적용 텍스트
        new_text: 규칙 적용 텍스트

    Returns:
        적용된 규칙 이름 리스트
    """
    applied_rules = []

    for rule_name, patterns in GRAMMAR_RULES.items():
        # 각 규칙을 old_text에 적용해서 변화가 있는지 확인
        test_text = old_text
        for pattern, replacement in patterns:
            test_text = re.sub(pattern, replacement, test_text)

        # old_text에 이 규칙을 적용했을 때 변화가 있으면
        if test_text != old_text:
            # new_text와 test_text가 유사한지 확인 (규칙이 적용됐는지)
            # 완전 일치가 아니라 규칙 패턴이 new_text에도 적용됐는지 확인
            new_test = old_text
            for pattern, replacement in patterns:
                new_test = re.sub(pattern, replacement, new_test)

            if new_test in new_text or re.search(r'|'.join([re.escape(p[1]) for p in patterns if isinstance(p[1], str) and p[1]]), new_text):
                applied_rules.append(rule_name)

    return applied_rules


def calculate_edit_distance(text1: str, text2: str) -> int:
    """
    두 텍스트 간 편집 거리 계산 (difflib 기반)

    Args:
        text1: 첫 번째 텍스트
        text2: 두 번째 텍스트

    Returns:
        편집 거리 (문자 단위 차이 개수)
    """
    # difflib을 사용하여 유사도 계산
    matcher = difflib.SequenceMatcher(None, text1, text2)
    # 편집 거리 = (전체 길이 - 일치하는 문자 수)
    matches = sum(block.size for block in matcher.get_matching_blocks())
    total_len = max(len(text1), len(text2))
    return total_len - matches


def analyze_rule_effects(
    version_comparison_path: Path,
    train_dataset_path: Path
) -> pd.DataFrame:
    """
    문법 규칙별 순효과 분석

    Args:
        version_comparison_path: version_comparison.csv 경로
        train_dataset_path: train_dataset.csv 경로

    Returns:
        규칙별 분석 결과 DataFrame
    """
    # 데이터 로드
    comparison_df = pd.read_csv(version_comparison_path)
    train_df = pd.read_csv(train_dataset_path)

    # ID로 매핑하여 정답 가져오기
    id_to_answer = dict(zip(train_df['err_sentence'], train_df['cor_sentence']))

    # 규칙별 효과 집계
    rule_stats = {rule_name: {'TP': 0, 'FP': 0, 'NC': 0, 'cases': []}
                  for rule_name in GRAMMAR_RULES.keys()}

    print(f"\n분석 시작: {len(comparison_df)}건")
    print("=" * 80)

    # 각 케이스 분석
    for idx, row in comparison_df.iterrows():
        err_sentence = row['err_sentence']
        old_correction = row['old_correction']
        new_correction = row['new_correction']

        # 정답 가져오기
        answer = id_to_answer.get(err_sentence)
        if answer is None:
            print(f"경고: {row['id']} 정답을 찾을 수 없음")
            continue

        # 편집 거리 계산
        old_dist = calculate_edit_distance(old_correction, answer)
        new_dist = calculate_edit_distance(new_correction, answer)

        # 적용된 규칙 감지
        applied_rules = detect_applied_rules(old_correction, new_correction)

        # 효과 판정
        if new_dist < old_dist:
            effect = 'TP'  # True Positive (개선)
        elif new_dist > old_dist:
            effect = 'FP'  # False Positive (악화)
        else:
            effect = 'NC'  # No Change (변화 없음)

        # 규칙별 집계
        for rule_name in applied_rules:
            rule_stats[rule_name][effect] += 1
            rule_stats[rule_name]['cases'].append({
                'id': row['id'],
                'old_dist': old_dist,
                'new_dist': new_dist,
                'effect': effect,
                'old': old_correction,
                'new': new_correction,
                'answer': answer
            })

        # 진행 상황 출력
        if (idx + 1) % 10 == 0:
            print(f"진행: {idx + 1}/{len(comparison_df)} 케이스 분석 완료")

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

    return result_df, rule_stats


def save_detailed_cases(rule_stats: Dict, output_dir: Path):
    """
    규칙별 상세 케이스를 개별 CSV로 저장

    Args:
        rule_stats: 규칙별 통계 딕셔너리
        output_dir: 출력 디렉토리
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    for rule_name, stats in rule_stats.items():
        if stats['cases']:
            cases_df = pd.DataFrame(stats['cases'])
            safe_name = rule_name.replace('/', '_').replace(' ', '_')
            output_path = output_dir / f"rule_cases_{safe_name}.csv"
            cases_df.to_csv(output_path, index=False, encoding='utf-8-sig')
            print(f"저장: {output_path} ({len(cases_df)}건)")


def analyze_train_rule_effects(
    no_rules_path: Path,
    with_rules_path: Path,
    train_path: Path
) -> pd.DataFrame:
    """
    Train 데이터에 대한 규칙별 효과 분석

    Args:
        no_rules_path: 규칙 미적용 버전 (메타데이터만 제거)
        with_rules_path: 규칙 적용 버전 (baseline.csv)
        train_path: Train 정답 데이터

    Returns:
        규칙별 분석 결과 DataFrame
    """
    # 데이터 로드
    no_rules_df = pd.read_csv(no_rules_path)
    with_rules_df = pd.read_csv(with_rules_path)
    train_df = pd.read_csv(train_path)

    print(f"규칙 OFF: {len(no_rules_df)}건")
    print(f"규칙 ON: {len(with_rules_df)}건")
    print(f"Train: {len(train_df)}건")

    # 정답 매핑
    id_to_answer = dict(zip(train_df['err_sentence'], train_df['cor_sentence']))

    # 규칙별 효과 집계
    rule_stats = {rule_name: {'TP': 0, 'FP': 0, 'NC': 0, 'cases': []}
                  for rule_name in GRAMMAR_RULES.keys()}

    print("\n분석 시작...")
    print("=" * 80)

    # 각 케이스 분석
    for idx in range(len(no_rules_df)):
        err_sentence = no_rules_df.loc[idx, 'err_sentence']
        no_rules_cor = no_rules_df.loc[idx, 'cor_sentence']
        with_rules_cor = with_rules_df.loc[idx, 'cor_sentence']

        # 정답 가져오기
        answer = id_to_answer.get(err_sentence)
        if answer is None:
            continue

        # 두 버전이 같으면 규칙이 적용 안 된 것
        if no_rules_cor == with_rules_cor:
            continue

        # 편집 거리 계산
        no_rules_dist = calculate_edit_distance(no_rules_cor, answer)
        with_rules_dist = calculate_edit_distance(with_rules_cor, answer)

        # 적용된 규칙 감지
        applied_rules = detect_applied_rules(no_rules_cor, with_rules_cor)

        # 효과 판정
        if with_rules_dist < no_rules_dist:
            effect = 'TP'  # True Positive (개선)
        elif with_rules_dist > no_rules_dist:
            effect = 'FP'  # False Positive (악화)
        else:
            effect = 'NC'  # No Change (변화 없음)

        # 규칙별 집계
        for rule_name in applied_rules:
            rule_stats[rule_name][effect] += 1
            rule_stats[rule_name]['cases'].append({
                'idx': idx,
                'err': err_sentence[:100],
                'no_rules': no_rules_cor[:100],
                'with_rules': with_rules_cor[:100],
                'answer': answer[:100],
                'no_rules_dist': no_rules_dist,
                'with_rules_dist': with_rules_dist,
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

    return result_df, rule_stats


def main():
    """메인 실행 함수"""
    # 경로 설정
    code_dir = Path(__file__).parent
    no_rules_path = code_dir / "outputs" / "submissions" / "train" / "submission_baseline_no_rules.csv"
    with_rules_path = code_dir / "outputs" / "submissions" / "train" / "submission_baseline.csv"
    train_path = code_dir / "data" / "train.csv"
    output_dir = code_dir / "outputs" / "analysis"

    # 파일 존재 확인
    if not no_rules_path.exists():
        print(f"오류: {no_rules_path} 파일이 없습니다.")
        print("먼저 apply_minimal_postprocess.py를 실행하세요.")
        return
    if not with_rules_path.exists():
        print(f"오류: {with_rules_path} 파일이 없습니다.")
        return
    if not train_path.exists():
        print(f"오류: {train_path} 파일이 없습니다.")
        return

    print("\n" + "=" * 80)
    print("문법 규칙별 순효과 분석 시작")
    print("=" * 80)

    # 분석 실행
    result_df, rule_stats = analyze_train_rule_effects(
        no_rules_path, with_rules_path, train_path
    )

    # 결과 저장
    output_dir.mkdir(parents=True, exist_ok=True)
    result_path = output_dir / "grammar_rule_effects.csv"
    result_df.to_csv(result_path, index=False, encoding='utf-8-sig')
    print(f"\n✅ 분석 결과 저장: {result_path}")

    # 상세 케이스 저장
    print("\n[상세 케이스 저장]")
    save_detailed_cases(rule_stats, output_dir)

    print("\n" + "=" * 80)
    print("분석 완료!")
    print("=" * 80)


if __name__ == "__main__":
    main()
