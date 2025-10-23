"""
Train 데이터 성능 비교

목적: 기존 버전 vs 신규 버전 성능 차이 확인
"""

import pandas as pd
import difflib


def calculate_edit_distance(text1: str, text2: str) -> int:
    """Edit distance 계산"""
    matcher = difflib.SequenceMatcher(None, text1, text2)
    matches = sum(block.size for block in matcher.get_matching_blocks())
    total_len = max(len(text1), len(text2))
    return total_len - matches


def calculate_recall(err_sentences, gold_sentences, pred_sentences):
    """
    Recall 계산 (GEC 대회 기준)

    TP: 교정이 필요하고 올바르게 교정한 경우
    FP: 교정이 필요없는데 교정한 경우
    FN: 교정이 필요한데 교정하지 못한 경우
    """
    tp = 0
    fp = 0
    fn = 0

    for err, gold, pred in zip(err_sentences, gold_sentences, pred_sentences):
        # 교정이 필요한가? (err != gold)
        needs_correction = (err != gold)

        # 교정했는가? (err != pred)
        was_corrected = (err != pred)

        # 올바르게 교정했는가? (pred == gold)
        correctly_corrected = (pred == gold)

        if needs_correction:
            if correctly_corrected:
                tp += 1  # 필요하고, 올바르게 교정
            else:
                fn += 1  # 필요한데, 잘못 교정하거나 미교정
        else:
            if was_corrected:
                fp += 1  # 불필요한데 교정함

    total = tp + fp + fn
    recall = (tp / total * 100) if total > 0 else 0.0
    precision = (tp / (tp + fp) * 100) if (tp + fp) > 0 else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

    return {
        'tp': tp,
        'fp': fp,
        'fn': fn,
        'recall': recall,
        'precision': precision,
        'f1': f1
    }


def main():
    print(f"\n{'='*80}")
    print(f"Train 데이터 성능 비교")
    print(f"{'='*80}\n")

    # Train 데이터 로드
    train = pd.read_csv('data/train.csv')

    # 기존 버전 (baseline with rules) - 가장 최근 것 찾기
    # submission_baseline.csv가 있는지 확인
    try:
        old_train = pd.read_csv('outputs/submissions/train/submission_baseline.csv')
        old_name = "submission_baseline.csv (with rules)"
    except:
        # 다른 버전 시도
        try:
            old_train = pd.read_csv('outputs/submissions/train/submission_baseline_test_clean.csv')
            old_name = "submission_baseline_test_clean.csv"
        except:
            print("⚠️ 기존 버전 파일을 찾을 수 없습니다.")
            return

    # 새 버전 (no rules version)
    try:
        new_train = pd.read_csv('outputs/submissions/train/submission_baseline_no_rules.csv')
        new_name = "submission_baseline_no_rules.csv"
    except:
        print("⚠️ 새 버전 파일을 찾을 수 없습니다.")
        return

    print(f"[비교 대상]")
    print(f"기존: {old_name}")
    print(f"신규: {new_name}")
    print()

    # 기존 버전 평가
    old_metrics = calculate_recall(
        train['err_sentence'].tolist(),
        train['cor_sentence'].tolist(),
        old_train['cor_sentence'].tolist()
    )

    print(f"[기존 버전 성능]")
    print(f"  TP: {old_metrics['tp']}")
    print(f"  FP: {old_metrics['fp']}")
    print(f"  FN: {old_metrics['fn']}")
    print(f"  Recall: {old_metrics['recall']:.2f}%")
    print(f"  Precision: {old_metrics['precision']:.2f}%")
    print(f"  F1: {old_metrics['f1']:.2f}%")
    print()

    # 새 버전 평가
    new_metrics = calculate_recall(
        train['err_sentence'].tolist(),
        train['cor_sentence'].tolist(),
        new_train['cor_sentence'].tolist()
    )

    print(f"[새 버전 성능]")
    print(f"  TP: {new_metrics['tp']}")
    print(f"  FP: {new_metrics['fp']}")
    print(f"  FN: {new_metrics['fn']}")
    print(f"  Recall: {new_metrics['recall']:.2f}%")
    print(f"  Precision: {new_metrics['precision']:.2f}%")
    print(f"  F1: {new_metrics['f1']:.2f}%")
    print()

    print(f"[차이 (새 - 기존)]")
    print(f"  TP: {new_metrics['tp'] - old_metrics['tp']:+d}")
    print(f"  FP: {new_metrics['fp'] - old_metrics['fp']:+d}")
    print(f"  FN: {new_metrics['fn'] - old_metrics['fn']:+d}")
    print(f"  Recall: {new_metrics['recall'] - old_metrics['recall']:+.2f}%p")
    print(f"  Precision: {new_metrics['precision'] - old_metrics['precision']:+.2f}%p")
    print(f"  F1: {new_metrics['f1'] - old_metrics['f1']:+.2f}%p")
    print()

    # 요약
    if new_metrics['recall'] > old_metrics['recall']:
        print("✅ 새 버전이 Train 성능 개선")
    elif new_metrics['recall'] < old_metrics['recall']:
        print("⚠️ 새 버전이 Train 성능 하락")
        print(f"   하지만 Test LB도 하락 ({31.91:.2f}% vs {34.04:.2f}%)")
        print("   → API 랜덤성 및 메타데이터 제거 불완전이 원인")
    else:
        print("➡️ Train 성능 동일")


if __name__ == "__main__":
    main()
