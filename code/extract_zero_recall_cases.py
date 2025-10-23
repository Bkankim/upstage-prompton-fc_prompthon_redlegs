"""
Recall 0% 유형 데이터 추출 스크립트

이전 분석(analyze_error_type_performance.py)에서 식별된
Recall 0%인 오류 유형들의 실제 케이스를 추출하여
Few-shot 예시 선정에 활용합니다.
"""

import pandas as pd
import json
from pathlib import Path

def extract_zero_recall_cases():
    """Recall 0% 유형의 케이스 추출 및 분석"""

    # 데이터 로드
    train_path = Path(__file__).parent / "data" / "train.csv"
    train_df = pd.read_csv(train_path)

    # Recall 0% 유형 목록 (이전 분석 결과 기반)
    zero_recall_types = [
        '비문',
        '문장부호',
        '능동피동',
        '누락',
        '중복',
        '논리오류',
        '띄어쓰기',
        '외래어'
    ]

    # 유형별 케이스 추출
    extracted_cases = {}

    for error_type in zero_recall_types:
        # 해당 유형의 케이스 필터링
        type_cases = train_df[train_df['type'] == error_type].copy()

        # 케이스 정보 수집
        cases = []
        for idx, row in type_cases.iterrows():
            case_info = {
                'index': idx,
                'err_sentence': row['err_sentence'],
                'cor_sentence': row['cor_sentence'],
                'type': row['type'],
                'original_target_part': row['original_target_part'],
                'golden_target_part': row['golden_target_part'],
                'err_length': len(row['err_sentence']),
                'cor_length': len(row['cor_sentence'])
            }
            cases.append(case_info)

        extracted_cases[error_type] = {
            'count': len(cases),
            'cases': cases
        }

        # 콘솔 출력
        print(f"\n{'='*60}")
        print(f"오류 유형: {error_type} (총 {len(cases)}건)")
        print(f"{'='*60}")

        for i, case in enumerate(cases, 1):
            print(f"\n[{i}] Index: {case['index']}")
            print(f"원문: {case['err_sentence']}")
            print(f"정답: {case['cor_sentence']}")
            print(f"오류부분: {case['original_target_part']} → {case['golden_target_part']}")
            print(f"길이: {case['err_length']} → {case['cor_length']} "
                  f"({case['cor_length'] - case['err_length']:+d})")

    # 통계 요약
    print(f"\n{'='*60}")
    print("전체 통계 요약")
    print(f"{'='*60}")
    total_cases = sum(info['count'] for info in extracted_cases.values())
    print(f"총 Recall 0% 케이스: {total_cases}건")
    for error_type, info in extracted_cases.items():
        print(f"  - {error_type}: {info['count']}건")

    # JSON 파일로 저장
    output_dir = Path(__file__).parent / "outputs" / "analysis"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "zero_recall_cases.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(extracted_cases, f, ensure_ascii=False, indent=2)

    print(f"\n결과 저장: {output_path}")

    return extracted_cases

if __name__ == "__main__":
    extract_zero_recall_cases()
