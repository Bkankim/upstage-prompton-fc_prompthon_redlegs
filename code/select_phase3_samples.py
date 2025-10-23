"""
Phase 3 샘플 선정 스크립트

목표:
- 50-60개 샘플 선정 (유형별 균형 유지)
- 이전 18개 검증 샘플 제외
- 유형별 3-5개씩 균등 배분 (샘플 적은 유형은 최대한)
"""

import pandas as pd
import random
from pathlib import Path


def select_phase3_samples():
    """
    Phase 3 확대 검증용 50-60개 샘플 선정

    전략:
    - 유형별 균형 유지
    - 이전 18개 검증 샘플 제외
    - 샘플 적은 유형: 최대한 선정
    - 샘플 많은 유형: 3-5개 선정
    """
    # 데이터 로드
    train_df = pd.read_csv(Path(__file__).parent / "data" / "train.csv")

    # 이전 18개 검증 샘플 (제외 대상)
    validation_18_indices = [2, 8, 10, 19, 26, 50, 59, 62, 64, 75, 99, 103, 123, 174, 208, 210, 245, 249]

    # 남은 샘플
    remaining_df = train_df[~train_df.index.isin(validation_18_indices)].copy()

    print("="*70)
    print("Phase 3 샘플 선정")
    print("="*70)
    print()
    print(f"전체 샘플: {len(train_df)}개")
    print(f"이전 검증 샘플: {len(validation_18_indices)}개")
    print(f"남은 샘플: {len(remaining_df)}개")
    print()

    # 유형별 남은 샘플 수
    remaining_type_counts = remaining_df['type'].value_counts().sort_values()

    print("유형별 남은 샘플:")
    for error_type, count in remaining_type_counts.items():
        print(f"  {error_type}: {count}개")
    print()

    # 샘플 선정 전략
    selected_indices = []
    selection_log = []

    for error_type, count in remaining_type_counts.items():
        type_df = remaining_df[remaining_df['type'] == error_type]
        type_indices = type_df.index.tolist()

        # 샘플 수에 따라 선정 개수 결정
        if count <= 3:
            # 3개 이하: 모두 선정
            n_select = count
        elif count <= 10:
            # 4-10개: 3개 선정
            n_select = 3
        elif count <= 20:
            # 11-20개: 4개 선정
            n_select = 4
        else:
            # 21개 이상: 5개 선정
            n_select = 5

        # 랜덤 선정
        selected = random.sample(type_indices, n_select)
        selected_indices.extend(selected)

        selection_log.append({
            'type': error_type,
            'available': count,
            'selected': n_select,
            'indices': selected
        })

    # 선정 결과 출력
    print("="*70)
    print("선정 결과")
    print("="*70)
    print()
    print(f"총 선정 샘플: {len(selected_indices)}개")
    print()

    print("유형별 선정 내역:")
    for log in selection_log:
        print(f"  {log['type']}: {log['selected']}개 선정 (남은 {log['available']}개 중)")
    print()

    # 선정된 샘플 DataFrame
    selected_df = train_df.loc[selected_indices].copy()

    # 유형별 분포 확인
    print("선정된 샘플 유형별 분포:")
    selected_type_counts = selected_df['type'].value_counts().sort_index()
    for error_type, count in selected_type_counts.items():
        print(f"  {error_type}: {count}개")
    print()

    # 인덱스 정렬 (가독성)
    selected_indices_sorted = sorted(selected_indices)

    print(f"선정된 인덱스 (정렬됨): {selected_indices_sorted[:10]}... (총 {len(selected_indices)}개)")
    print()

    # 결과 저장
    output_dir = Path(__file__).parent / "outputs" / "experiments"
    output_dir.mkdir(parents=True, exist_ok=True)

    # 선정 인덱스 저장 (JSON)
    import json
    with open(output_dir / "phase3_selected_indices.json", 'w', encoding='utf-8') as f:
        json.dump({
            'total_selected': len(selected_indices),
            'selected_indices': selected_indices_sorted,
            'selection_log': selection_log,
            'excluded_indices': validation_18_indices
        }, f, ensure_ascii=False, indent=2)

    # 선정 샘플 DataFrame 저장 (CSV)
    selected_df.to_csv(
        output_dir / "phase3_selected_samples.csv",
        index=True,
        encoding='utf-8'
    )

    print(f"결과 저장 완료:")
    print(f"  - {output_dir / 'phase3_selected_indices.json'}")
    print(f"  - {output_dir / 'phase3_selected_samples.csv'}")
    print()

    # 검증
    if 50 <= len(selected_indices) <= 60:
        print("✅ 목표 달성: 50-60개 샘플 선정 완료")
    else:
        print(f"⚠️ 목표 범위 벗어남: {len(selected_indices)}개 (목표: 50-60개)")

    return selected_indices_sorted, selected_df


if __name__ == "__main__":
    # 재현성을 위한 시드 고정
    random.seed(42)

    selected_indices, selected_df = select_phase3_samples()
