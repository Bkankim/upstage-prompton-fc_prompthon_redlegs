"""
데이터셋 분석 스크립트
- 오류 유형별 통계
- 패턴 분석
- 샘플 확인
"""

import pandas as pd
import json

def analyze_train_data():
    """학습 데이터 분석 함수"""

    # 데이터 로드
    train_df = pd.read_csv('/Competition/upstage-prompton-fc_prompthon_redlegs/data/train.csv')
    test_df = pd.read_csv('/Competition/upstage-prompton-fc_prompthon_redlegs/data/test.csv')

    print("=" * 60)
    print("데이터셋 기본 정보")
    print("=" * 60)
    print(f"학습 데이터: {train_df.shape[0]}개 문장, {train_df.shape[1]}개 컬럼")
    print(f"테스트 데이터: {test_df.shape[0]}개 문장, {test_df.shape[1]}개 컬럼")
    print()

    # 컬럼 정보
    print("학습 데이터 컬럼:")
    print(train_df.columns.tolist())
    print()
    print("테스트 데이터 컬럼:")
    print(test_df.columns.tolist())
    print()

    print("=" * 60)
    print("오류 유형별 분포")
    print("=" * 60)
    type_counts = train_df['type'].value_counts()
    for error_type, count in type_counts.items():
        percentage = (count / len(train_df)) * 100
        print(f"{error_type:20} : {count:3d}개 ({percentage:5.1f}%)")
    print()

    print("=" * 60)
    print("오류 유형별 샘플 (각 2개씩)")
    print("=" * 60)
    for error_type in type_counts.index:
        print(f"\n[{error_type}]")
        samples = train_df[train_df['type'] == error_type].head(2)
        for idx, row in samples.iterrows():
            print(f"  원문: {row['err_sentence'][:100]}")
            print(f"  교정: {row['cor_sentence'][:100]}")
            print(f"  오류부분: '{row['original_target_part']}' → '{row['golden_target_part']}'")
            print()

    # 문장 길이 분석
    print("=" * 60)
    print("문장 길이 통계")
    print("=" * 60)
    train_df['err_len'] = train_df['err_sentence'].str.len()
    train_df['cor_len'] = train_df['cor_sentence'].str.len()

    print(f"원문 평균 길이: {train_df['err_len'].mean():.1f} 자")
    print(f"원문 최소 길이: {train_df['err_len'].min()} 자")
    print(f"원문 최대 길이: {train_df['err_len'].max()} 자")
    print()

    # 교정 전후 변화
    print("=" * 60)
    print("교정 전후 변화 패턴")
    print("=" * 60)
    train_df['len_diff'] = train_df['cor_len'] - train_df['err_len']
    print(f"길이 변화 없음: {(train_df['len_diff'] == 0).sum()}개")
    print(f"길이 증가: {(train_df['len_diff'] > 0).sum()}개")
    print(f"길이 감소: {(train_df['len_diff'] < 0).sum()}개")
    print()

    # 자주 나오는 오류 패턴
    print("=" * 60)
    print("자주 나오는 교정 패턴 (Top 10)")
    print("=" * 60)
    corrections = []
    for _, row in train_df.iterrows():
        if pd.notna(row['original_target_part']) and pd.notna(row['golden_target_part']):
            corrections.append(f"{row['original_target_part']} → {row['golden_target_part']}")

    from collections import Counter
    pattern_counts = Counter(corrections)
    for pattern, count in pattern_counts.most_common(10):
        print(f"  {pattern:40} : {count}회")

    print()
    print("=" * 60)
    print("분석 완료")
    print("=" * 60)

if __name__ == "__main__":
    analyze_train_data()