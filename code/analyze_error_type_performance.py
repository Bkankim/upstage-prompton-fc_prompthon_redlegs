"""
Phase 3.2: 유형별 성과 분석

목적: 오류 유형별 Recall/Precision 계산 및 취약 유형 식별
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from collections import defaultdict


def calculate_recall_by_type(
    train_csv: str = "data/train.csv",
    submission_csv: str = "outputs/submissions/train/submission_baseline.csv"
):
    """
    오류 유형별 Recall/Precision 계산

    Args:
        train_csv: Train 데이터 (정답 포함)
        submission_csv: 교정 결과

    Returns:
        dict: 유형별 성과 데이터
    """
    print(f"\n{'='*80}")
    print(f"Phase 3.2: 유형별 성과 분석")
    print(f"{'='*80}\n")

    # 데이터 로드
    train = pd.read_csv(train_csv)
    submission = pd.read_csv(submission_csv)

    print(f"데이터 로드:")
    print(f"  Train: {len(train)}개")
    print(f"  Submission: {len(submission)}개")
    print()

    # 오류 유형별 분류
    type_stats = defaultdict(lambda: {
        'total': 0,
        'tp': 0,
        'fp': 0,
        'fn': 0,
        'cases': []
    })

    # 각 케이스 평가
    for idx in range(len(train)):
        err_sentence = train.iloc[idx]['err_sentence']
        gold_sentence = train.iloc[idx]['cor_sentence']
        pred_sentence = submission.iloc[idx]['cor_sentence']
        error_type = train.iloc[idx]['type']

        # 교정이 필요한가?
        needs_correction = (err_sentence != gold_sentence)

        # 교정했는가?
        was_corrected = (err_sentence != pred_sentence)

        # 올바르게 교정했는가?
        correctly_corrected = (pred_sentence == gold_sentence)

        # 카운트
        type_stats[error_type]['total'] += 1

        if needs_correction:
            if correctly_corrected:
                type_stats[error_type]['tp'] += 1
                result = 'TP'
            else:
                type_stats[error_type]['fn'] += 1
                result = 'FN'
        else:
            if was_corrected:
                type_stats[error_type]['fp'] += 1
                result = 'FP'
            else:
                result = 'TN'

        # 케이스 기록
        type_stats[error_type]['cases'].append({
            'index': idx,
            'result': result,
            'err_sentence': err_sentence[:50],
            'gold_sentence': gold_sentence[:50],
            'pred_sentence': pred_sentence[:50]
        })

    # 유형별 Recall/Precision 계산
    type_performance = []

    for error_type, stats in type_stats.items():
        tp = stats['tp']
        fp = stats['fp']
        fn = stats['fn']
        total = stats['total']

        # Recall = TP / (TP + FP + FN)
        recall = (tp / (tp + fp + fn) * 100) if (tp + fp + fn) > 0 else 0.0

        # Precision = TP / (TP + FP)
        precision = (tp / (tp + fp) * 100) if (tp + fp) > 0 else 0.0

        # F1 Score
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

        type_performance.append({
            'error_type': error_type,
            'total_cases': total,
            'tp': tp,
            'fp': fp,
            'fn': fn,
            'recall': recall,
            'precision': precision,
            'f1': f1
        })

    # DataFrame 생성
    df = pd.DataFrame(type_performance)
    df = df.sort_values('recall', ascending=False)

    # 통계 계산
    mean_recall = df['recall'].mean()
    std_recall = df['recall'].std()
    mean_precision = df['precision'].mean()
    std_precision = df['precision'].std()

    print(f"[전체 통계]")
    print(f"{'='*80}")
    print(f"오류 유형 수: {len(df)}")
    print(f"평균 Recall: {mean_recall:.2f}% ± {std_recall:.2f}%")
    print(f"평균 Precision: {mean_precision:.2f}% ± {std_precision:.2f}%")
    print()

    # 취약 유형 식별 (평균 - 1σ 이하)
    weak_threshold = mean_recall - std_recall
    strong_threshold = mean_recall + std_recall

    df['category'] = df['recall'].apply(
        lambda r: '강점' if r > strong_threshold else ('취약' if r < weak_threshold else '보통')
    )

    weak_types = df[df['category'] == '취약']
    strong_types = df[df['category'] == '강점']

    print(f"[취약 유형 (Recall < {weak_threshold:.2f}%)]")
    print(f"{'='*80}")
    if len(weak_types) > 0:
        for idx, row in weak_types.iterrows():
            print(f"⚠️ {row['error_type']}")
            print(f"   Recall: {row['recall']:.2f}% (평균 - {mean_recall - row['recall']:.2f}%p)")
            print(f"   케이스: {row['total_cases']}개 (TP={row['tp']}, FP={row['fp']}, FN={row['fn']})")
            print()
    else:
        print("없음")

    print(f"[강점 유형 (Recall > {strong_threshold:.2f}%)]")
    print(f"{'='*80}")
    if len(strong_types) > 0:
        for idx, row in strong_types.iterrows():
            print(f"✅ {row['error_type']}")
            print(f"   Recall: {row['recall']:.2f}% (평균 + {row['recall'] - mean_recall:.2f}%p)")
            print(f"   케이스: {row['total_cases']}개 (TP={row['tp']}, FP={row['fp']}, FN={row['fn']})")
            print()
    else:
        print("없음")

    print(f"[전체 유형별 성과]")
    print(f"{'='*80}")
    print(df.to_string(index=False))
    print()

    # 결과 저장 (CSV)
    output_csv = "outputs/analysis/error_type_performance.csv"
    Path(output_csv).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv, index=False, encoding='utf-8-sig')

    print(f"CSV 저장: {output_csv}")

    # 결과 저장 (JSON)
    result = {
        'analysis_date': '2025-10-23',
        'data_source': {
            'train': train_csv,
            'submission': submission_csv
        },
        'statistics': {
            'total_types': len(df),
            'mean_recall': float(mean_recall),
            'std_recall': float(std_recall),
            'mean_precision': float(mean_precision),
            'std_precision': float(std_precision),
            'weak_threshold': float(weak_threshold),
            'strong_threshold': float(strong_threshold)
        },
        'weak_types': weak_types[['error_type', 'recall', 'total_cases', 'tp', 'fp', 'fn']].to_dict('records'),
        'strong_types': strong_types[['error_type', 'recall', 'total_cases', 'tp', 'fp', 'fn']].to_dict('records'),
        'all_types': df.to_dict('records')
    }

    output_json = "outputs/logs/experiments/phase3_error_type_analysis.json"
    Path(output_json).parent.mkdir(parents=True, exist_ok=True)
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"JSON 저장: {output_json}")
    print()

    # 권장 사항
    print(f"[권장 사항]")
    print(f"{'='*80}")

    if len(weak_types) > 0:
        print(f"1. 취약 유형 Few-shot 보강:")
        for idx, row in weak_types.iterrows():
            print(f"   - {row['error_type']}: {row['total_cases']}개 케이스에서 Few-shot 추가")
        print()

    if len(weak_types) > 3:
        print(f"2. 프롬프트 개선:")
        print(f"   - 취약 유형이 {len(weak_types)}개로 많음")
        print(f"   - 전체적인 프롬프트 개선 필요")
        print()

    print(f"3. 일반화 전략:")
    print(f"   - 취약 유형의 분산이 높으면 Private LB에 불리")
    print(f"   - 유형별 균형 개선이 일반화에 도움")
    print()

    return result


if __name__ == "__main__":
    result = calculate_recall_by_type()

    print(f"\n{'='*80}")
    print(f"Phase 3.2 완료")
    print(f"{'='*80}\n")

    print(f"다음 단계:")
    print(f"1. 취약 유형 Few-shot 보강")
    print(f"2. 프롬프트 형식 제약 A/B 실험")
    print(f"3. 5-fold 교차검증 (선택)")
    print()
