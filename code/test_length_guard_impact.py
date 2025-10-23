"""
60% 길이 가드 Dry-run 영향도 분석

목적: 현재 후처리 결과에서 60% 미만으로 줄어든 케이스 식별
"""

import pandas as pd
import json
from pathlib import Path


def calculate_length_ratio(original: str, corrected: str) -> float:
    """
    교정 후 길이 비율 계산

    Args:
        original: 원본 문장
        corrected: 교정된 문장

    Returns:
        float: 교정 후 길이 / 원본 길이 (0.0 ~ 1.0)
    """
    if not original or len(original) == 0:
        return 1.0

    return len(corrected) / len(original)


def analyze_length_guard_impact(
    train_csv: str = "data/train.csv",
    corrected_csv: str = "outputs/submissions/train/submission_baseline_no_rules.csv",
    threshold: float = 0.6,
    output_log: str = "outputs/logs/length_guard_impact.json"
):
    """
    60% 길이 가드 영향도 분석

    Args:
        train_csv: 원본 학습 데이터 경로
        corrected_csv: 교정된 데이터 경로
        threshold: 길이 가드 임계값 (기본 0.6 = 60%)
        output_log: 결과 로그 저장 경로
    """
    print(f"\n{'='*60}")
    print(f"60% 길이 가드 Dry-run 영향도 분석")
    print(f"{'='*60}\n")

    # 데이터 로드
    train_df = pd.read_csv(train_csv)
    corrected_df = pd.read_csv(corrected_csv)

    # 인덱스 기반 병합 (순서가 동일하다고 가정)
    merged = pd.DataFrame({
        'err_sentence': train_df['err_sentence'],
        'cor_sentence_original': train_df['cor_sentence'],
        'cor_sentence': corrected_df['cor_sentence']
    })
    merged['id'] = merged.index

    # 길이 비율 계산
    merged['length_ratio'] = merged.apply(
        lambda row: calculate_length_ratio(row['err_sentence'], row['cor_sentence']),
        axis=1
    )

    # 60% 미만 케이스 식별
    rollback_cases = merged[merged['length_ratio'] < threshold].copy()

    # 통계 계산
    total_cases = len(merged)
    rollback_count = len(rollback_cases)
    rollback_ratio = (rollback_count / total_cases) * 100

    # 결과 출력
    print(f"전체 케이스: {total_cases}개")
    print(f"롤백 대상: {rollback_count}개")
    print(f"롤백 비율: {rollback_ratio:.2f}%")
    print(f"임계값: {threshold*100:.0f}%\n")

    # 목표 달성 여부
    target_ratio = 5.0
    if rollback_ratio < target_ratio:
        print(f"✅ 목표 달성! (목표: {target_ratio}% 미만)")
    else:
        print(f"⚠️ 목표 미달! (목표: {target_ratio}% 미만)")
        print(f"   권장: 임계값을 {threshold-0.05:.0%} 또는 {threshold+0.05:.0%}로 조정 검토\n")

    # 롤백 케이스 상세 분석
    if rollback_count > 0:
        print(f"\n[롤백 케이스 상세]")
        print(f"{'='*60}\n")

        rollback_details = []

        for idx, row in rollback_cases.iterrows():
            detail = {
                'id': int(row['id']),
                'original_length': len(row['err_sentence']),
                'corrected_length': len(row['cor_sentence']),
                'length_ratio': float(row['length_ratio']),
                'err_sentence': row['err_sentence'],
                'cor_sentence': row['cor_sentence']
            }
            rollback_details.append(detail)

            print(f"ID: {detail['id']}")
            print(f"길이 비율: {detail['length_ratio']:.1%} ({detail['original_length']} → {detail['corrected_length']})")
            print(f"원본: {detail['err_sentence']}")
            print(f"교정: {detail['cor_sentence']}")
            print()

    # 결과 저장
    result = {
        'analysis_config': {
            'train_csv': train_csv,
            'corrected_csv': corrected_csv,
            'threshold': threshold
        },
        'statistics': {
            'total_cases': total_cases,
            'rollback_count': rollback_count,
            'rollback_ratio': rollback_ratio,
            'target_achieved': rollback_ratio < target_ratio
        },
        'rollback_cases': rollback_details if rollback_count > 0 else []
    }

    # 로그 디렉토리 생성
    Path(output_log).parent.mkdir(parents=True, exist_ok=True)

    # JSON 저장
    with open(output_log, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"{'='*60}")
    print(f"결과 저장: {output_log}")
    print(f"{'='*60}\n")

    return result


def test_different_thresholds():
    """
    여러 임계값으로 테스트
    """
    print(f"\n{'='*60}")
    print(f"다양한 임계값 테스트")
    print(f"{'='*60}\n")

    thresholds = [0.55, 0.60, 0.65]
    results = []

    for threshold in thresholds:
        print(f"\n[임계값: {threshold*100:.0f}%]")
        print("-" * 60)

        # 간단한 분석
        train_df = pd.read_csv("data/train.csv")
        corrected_df = pd.read_csv("outputs/submissions/train/submission_baseline_no_rules.csv")

        merged = pd.DataFrame({
            'err_sentence': train_df['err_sentence'],
            'cor_sentence': corrected_df['cor_sentence']
        })

        merged['length_ratio'] = merged.apply(
            lambda row: calculate_length_ratio(row['err_sentence'], row['cor_sentence']),
            axis=1
        )

        rollback_count = len(merged[merged['length_ratio'] < threshold])
        rollback_ratio = (rollback_count / len(merged)) * 100

        results.append({
            'threshold': threshold,
            'rollback_count': rollback_count,
            'rollback_ratio': rollback_ratio
        })

        print(f"롤백 대상: {rollback_count}개 ({rollback_ratio:.2f}%)")

    print(f"\n{'='*60}")
    print(f"임계값 비교 요약")
    print(f"{'='*60}\n")

    for result in results:
        status = "✅" if result['rollback_ratio'] < 5.0 else "⚠️"
        print(f"{status} {result['threshold']*100:.0f}%: {result['rollback_count']}개 ({result['rollback_ratio']:.2f}%)")


if __name__ == "__main__":
    # 기본 60% 임계값 분석
    result = analyze_length_guard_impact()

    # 다양한 임계값 테스트
    test_different_thresholds()
