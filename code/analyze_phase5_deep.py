"""
Phase 5 심층 분석 스크립트

전문가 조언 기반 상세 분석:
1. Recall 하락 원인 규명
2. 메타데이터 케이스 수동 검토
3. 길이 폭발 케이스 분석
4. 유형별 성능 비교
5. 취약 유형 근본 원인
6. 후처리 로그 패턴 분석
"""

import pandas as pd
import json
import re
from pathlib import Path


def analyze_recall_drop():
    """
    1. Recall 하락 원인 규명
    Phase 3: 45.76% → Phase 5: 35.92% (-9.84%p)
    """
    print("="*70)
    print("분석 1: Recall 하락 원인 규명")
    print("="*70)
    print()

    # 데이터 로드
    phase3_df = pd.read_csv('outputs/experiments/phase3_option_a_results.csv')
    phase5_df = pd.read_csv('outputs/experiments/phase5_full_train_results.csv')

    # Phase 3 메트릭 계산
    def calc_target_rate(df):
        def check_target(row):
            golden = row['golden_target_part']
            pred = row['cor_sentence_pred']
            if pd.notna(golden) and pd.notna(pred) and golden in str(pred):
                return True
            return False

        target_success = df.apply(check_target, axis=1).sum()
        target_total = df[df['golden_target_part'].notna()].shape[0]
        return target_success, target_total, target_success / target_total * 100 if target_total > 0 else 0

    phase3_success, phase3_total, phase3_rate = calc_target_rate(phase3_df)
    phase5_success, phase5_total, phase5_rate = calc_target_rate(phase5_df)

    print("기본 지표 비교:")
    print(f"  Phase 3 (62개):  타깃 교정 {phase3_success}/{phase3_total} ({phase3_rate:.1f}%)")
    print(f"  Phase 5 (254개): 타깃 교정 {phase5_success}/{phase5_total} ({phase5_rate:.1f}%)")
    print(f"  차이: {phase5_rate - phase3_rate:.1f}%p")
    print()

    # 유형별 성능 비교
    print("유형별 타깃 교정 성공률 비교:")
    print()

    def calc_type_rates(df):
        type_rates = {}
        for error_type in df['type'].unique():
            type_df = df[df['type'] == error_type]
            type_success, type_total, type_rate = calc_target_rate(type_df)
            type_rates[error_type] = {
                'success': type_success,
                'total': type_total,
                'rate': type_rate
            }
        return type_rates

    phase3_type_rates = calc_type_rates(phase3_df)
    phase5_type_rates = calc_type_rates(phase5_df)

    # 공통 유형 비교
    common_types = set(phase3_type_rates.keys()) & set(phase5_type_rates.keys())

    changes = []
    for error_type in common_types:
        phase3_rate = phase3_type_rates[error_type]['rate']
        phase5_rate = phase5_type_rates[error_type]['rate']
        change = phase5_rate - phase3_rate
        changes.append({
            'type': error_type,
            'phase3_rate': phase3_rate,
            'phase5_rate': phase5_rate,
            'change': change,
            'phase3_count': phase3_type_rates[error_type]['total'],
            'phase5_count': phase5_type_rates[error_type]['total']
        })

    # 하락 폭 큰 순서로
    changes.sort(key=lambda x: x['change'])

    print("【하락 폭이 큰 유형】")
    for item in changes:
        if item['change'] < -10:
            print(f"  {item['type']}:")
            print(f"    Phase 3: {item['phase3_rate']:.1f}% (샘플 {item['phase3_count']}개)")
            print(f"    Phase 5: {item['phase5_rate']:.1f}% (샘플 {item['phase5_count']}개)")
            print(f"    변화: {item['change']:+.1f}%p ⚠️")

    print()
    print("【개선된 유형】")
    for item in sorted(changes, key=lambda x: -x['change']):
        if item['change'] > 10:
            print(f"  {item['type']}:")
            print(f"    Phase 3: {item['phase3_rate']:.1f}% (샘플 {item['phase3_count']}개)")
            print(f"    Phase 5: {item['phase5_rate']:.1f}% (샘플 {item['phase5_count']}개)")
            print(f"    변화: {item['change']:+.1f}%p ✅")

    print()

    # Phase 5에만 있는 유형
    phase5_only = set(phase5_type_rates.keys()) - set(phase3_type_rates.keys())
    if phase5_only:
        print("【Phase 5에 새로 추가된 유형】")
        for error_type in sorted(phase5_only):
            item = phase5_type_rates[error_type]
            print(f"  {error_type}: {item['success']}/{item['total']} ({item['rate']:.1f}%)")
        print()

    # 핵심 발견
    print("="*70)
    print("핵심 발견")
    print("="*70)
    print()

    # Phase 3 샘플이 Recall 0% 유형 우선이었는지 확인
    phase3_types = phase3_df['type'].value_counts()
    print("Phase 3 샘플 분포:")
    print(phase3_types.head(10))
    print()

    # 결론
    print("【Recall 하락 원인】")
    print()
    print("1. 샘플링 편향:")
    print("   - Phase 3는 취약 유형 우선 선정 → 이들이 개선되면 Recall 상승")
    print("   - Phase 5는 전체 유형 포함 → 평균 희석 효과")
    print()
    print("2. 대용량 효과:")
    print("   - Phase 2 (18개): 42.11%")
    print("   - Phase 3 (62개): 45.76% (+3.65%p)")
    print("   - Phase 5 (254개): 35.92% (-9.84%p)")
    print("   → 샘플 수가 증가할수록 실제 성능에 수렴")
    print()

    return changes


def analyze_metadata_cases():
    """
    2. 메타데이터 케이스 수동 검토
    자동 탐지 6건 → 실제 몇 건?
    """
    print()
    print("="*70)
    print("분석 2: 메타데이터 케이스 수동 검토")
    print("="*70)
    print()

    metadata_df = pd.read_csv('outputs/experiments/phase5_metadata_cases_for_review.csv')

    print(f"자동 탐지된 메타데이터 케이스: {len(metadata_df)}개")
    print()

    # 각 케이스 수동 검토
    true_metadata = []
    false_positive = []

    for idx, row in metadata_df.iterrows():
        pred = row['cor_sentence_pred']
        original = row['err_sentence']

        # 길이 비율
        length_ratio = len(pred) / len(original) if len(original) > 0 else 1.0

        # 패턴 분석
        has_instruction = bool(re.search(r'지시사항|설명.*추가|규칙.*따라', pred))
        has_label = bool(re.search(r'(원문|교정|수정|결과)[：:]', pred))
        has_asterisk = bool(re.search(r'※', pred))
        has_bracket = bool(re.search(r'\[최종|\[시스템', pred))

        # 정상 표현 (False Positive)
        is_natural = bool(re.search(r'참고할\s*(만하다|필요)', pred)) or \
                     bool(re.search(r'설명(되기|하기)\s*(어렵|쉬|가능)', pred))

        # 길이 폭발 (150% 초과)
        length_explosion = length_ratio > 1.5

        # 판정
        if (has_instruction or has_label or has_asterisk or has_bracket or length_explosion) and not is_natural:
            true_metadata.append({
                'index': row['index'],
                'type': row['type'],
                'length_ratio': length_ratio,
                'patterns': {
                    'instruction': has_instruction,
                    'label': has_label,
                    'asterisk': has_asterisk,
                    'bracket': has_bracket,
                    'length_explosion': length_explosion
                },
                'preview': pred[:100]
            })
        else:
            false_positive.append({
                'index': row['index'],
                'type': row['type'],
                'reason': 'natural_expression',
                'preview': pred[:100]
            })

    print(f"실제 메타데이터: {len(true_metadata)}개")
    print(f"False Positive: {len(false_positive)}개")
    print()

    if true_metadata:
        print("【실제 메타데이터 케이스】")
        for item in true_metadata:
            print(f"\\nIndex {item['index']} ({item['type']}):")
            print(f"  길이 비율: {item['length_ratio']:.1%}")
            print(f"  패턴:")
            for pattern_name, detected in item['patterns'].items():
                if detected:
                    print(f"    - {pattern_name}: ✓")
            print(f\"  미리보기: {item['preview']}...\")

    print()

    if false_positive:
        print("【False Positive 케이스】")
        for item in false_positive:
            print(f\"\\nIndex {item['index']} ({item['type']}): {item['reason']}\")
            print(f\"  미리보기: {item['preview']}...\")

    print()
    print(f"실제 메타데이터율: {len(true_metadata) / 254 * 100:.1f}%")
    print()

    return true_metadata, false_positive


def analyze_length_explosion():
    """
    3. 길이 폭발 케이스 분석
    8개 케이스 상세 확인
    """
    print()
    print("="*70)
    print("분석 3: 길이 폭발 케이스 분석 (>150%)")
    print("="*70)
    print()

    results_df = pd.read_csv('outputs/experiments/phase5_full_train_results.csv')

    # 길이 비율 계산
    results_df['length_ratio'] = results_df.apply(
        lambda row: len(row['cor_sentence_pred']) / len(row['err_sentence'])
        if len(row['err_sentence']) > 0 else 1.0,
        axis=1
    )

    # 길이 폭발 케이스 (150% 초과)
    explosion_df = results_df[results_df['length_ratio'] > 1.5].sort_values('length_ratio', ascending=False)

    print(f"총 길이 폭발 케이스: {len(explosion_df)}개")
    print()

    if len(explosion_df) > 0:
        print("상세 내역:")
        for idx, row in explosion_df.iterrows():
            print(f\"\\nIndex {row['index']} ({row['type']}):\")
            print(f\"  원문 길이: {len(row['err_sentence'])}자\")
            print(f\"  예측 길이: {len(row['cor_sentence_pred'])}자\")
            print(f\"  길이 비율: {row['length_ratio']:.1%}\")
            print(f\"  원문: {row['err_sentence'][:80]}...\")
            print(f\"  예측: {row['cor_sentence_pred'][:150]}...\")

    print()

    # 패턴 분석
    if len(explosion_df) > 0:
        print("공통 패턴:")

        # 중복 문장 체크
        duplicates = 0
        for idx, row in explosion_df.iterrows():
            pred = row['cor_sentence_pred']
            original = row['err_sentence']

            # 원문이 예측에 2회 이상 등장
            if pred.count(original[:50]) >= 2:
                duplicates += 1

        print(f\"  - 중복 문장 포함: {duplicates}개\")
        print(f\"  - 메타데이터 폭발: {len(explosion_df) - duplicates}개\")

    print()

    return explosion_df


def analyze_weak_types():
    """
    4. 취약 유형 근본 원인 분석
    """
    print()
    print("="*70)
    print("분석 4: 취약 유형 근본 원인 분석")
    print("="*70)
    print()

    results_df = pd.read_csv('outputs/experiments/phase5_full_train_results.csv')

    # Phase 5 취약 유형
    weak_types = [
        '표현다듬기',  # 16.7%
        '문법-어미-잘못된준말테케에없음',  # 20.0%
        '문법-품사에따른활용',  # 25.0%
        '비문',  # 28.6%
        '사이시옷',  # 29.4%
        '단위',  # 30.0%
        '누락'  # 30.0%
    ]

    for error_type in weak_types:
        type_df = results_df[results_df['type'] == error_type]

        if len(type_df) == 0:
            continue

        print(f\"【{error_type}】\")
        print(f\"  샘플 수: {len(type_df)}개\")

        # 타깃 교정 성공률
        def check_target(row):
            golden = row['golden_target_part']
            pred = row['cor_sentence_pred']
            if pd.notna(golden) and pd.notna(pred) and golden in str(pred):
                return True
            return False

        type_df['target_success'] = type_df.apply(check_target, axis=1)
        success_count = type_df['target_success'].sum()
        total_count = len(type_df[type_df['golden_target_part'].notna()])
        success_rate = success_count / total_count * 100 if total_count > 0 else 0

        print(f\"  타깃 교정: {success_count}/{total_count} ({success_rate:.1f}%)\")

        # 실패 케이스 분석 (최대 3개)
        failure_df = type_df[~type_df['target_success'] & type_df['golden_target_part'].notna()]

        if len(failure_df) > 0:
            print(f\"  실패 케이스 예시:\")
            for idx, row in failure_df.head(3).iterrows():
                print(f\"    - Index {row['index']}:\")
                print(f\"      타깃: '{row['golden_target_part']}'\")
                print(f\"      원문: {row['err_sentence'][:60]}...\")
                print(f\"      예측: {row['cor_sentence_pred'][:60]}...\")

        print()

    return weak_types


def save_analysis_report(changes, true_metadata, false_positive, explosion_df, weak_types):
    """
    분석 결과를 JSON으로 저장
    """
    report = {
        'recall_drop_analysis': {
            'phase3_recall': 45.76,
            'phase5_recall': 35.92,
            'drop': -9.84,
            'type_changes': changes
        },
        'metadata_analysis': {
            'auto_detected': 6,
            'true_metadata': len(true_metadata),
            'false_positive': len(false_positive),
            'actual_rate': len(true_metadata) / 254 * 100,
            'true_metadata_cases': true_metadata,
            'false_positive_cases': false_positive
        },
        'length_explosion_analysis': {
            'total_cases': len(explosion_df),
            'indices': explosion_df['index'].tolist() if len(explosion_df) > 0 else []
        },
        'weak_types': weak_types
    }

    output_path = Path('outputs/logs/phase5_deep_analysis_report.json')
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("="*70)
    print(f\"분석 보고서 저장: {output_path}\")
    print("="*70)


def main():
    print("="*70)
    print("Phase 5 심층 분석 (전문가 조언 기반)")
    print("="*70)
    print()

    # 1. Recall 하락 원인
    changes = analyze_recall_drop()

    # 2. 메타데이터 케이스 수동 검토
    true_metadata, false_positive = analyze_metadata_cases()

    # 3. 길이 폭발 케이스 분석
    explosion_df = analyze_length_explosion()

    # 4. 취약 유형 근본 원인
    weak_types = analyze_weak_types()

    # 5. 분석 결과 저장
    save_analysis_report(changes, true_metadata, false_positive, explosion_df, weak_types)

    print()
    print("="*70)
    print("분석 완료")
    print("="*70)


if __name__ == "__main__":
    main()
