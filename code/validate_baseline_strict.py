"""
baseline_strict 프롬프트 검증 스크립트

Train 데이터 20개 샘플로 형식 제약 효과 검증:
- Recall 0% 유형 각 1개 (8개)
- 기타 유형 랜덤 (12개)

목표:
- 메타데이터 출현 0%
- 텍스트 반복 0%
- 불필요한 수정 최소화
"""

import pandas as pd
import json
import random
from pathlib import Path
from src.generator import SentenceGenerator
from src.evaluator import Evaluator


def select_test_samples():
    """
    검증용 20개 샘플 선정

    Returns:
        list: 선정된 인덱스 리스트
    """
    # 데이터 로드
    train_df = pd.read_csv(Path(__file__).parent / "data" / "train.csv")

    # Recall 0% 유형 각 1개씩 선정
    zero_recall_types = [
        '비문', '문장부호', '능동피동', '누락',
        '중복', '논리오류', '띄어쓰기', '외래어'
    ]

    selected_indices = []

    # 각 유형에서 1개씩
    for error_type in zero_recall_types:
        type_indices = train_df[train_df['type'] == error_type].index.tolist()
        if type_indices:
            selected_indices.append(random.choice(type_indices))

    # 나머지 유형에서 12개 랜덤 선정
    remaining_indices = [
        i for i in train_df.index
        if i not in selected_indices
    ]
    selected_indices.extend(random.sample(remaining_indices, min(12, len(remaining_indices))))

    return sorted(selected_indices)


def validate_baseline_strict():
    """
    baseline_strict 프롬프트 검증 실행
    """
    print("="*60)
    print("baseline_strict 프롬프트 검증 시작")
    print("="*60)

    # 데이터 로드
    train_df = pd.read_csv(Path(__file__).parent / "data" / "train.csv")

    # 샘플 선정
    test_indices = select_test_samples()
    test_df = train_df.loc[test_indices].copy()

    print(f"\n선정된 샘플: {len(test_df)}개")
    print("\n유형별 분포:")
    print(test_df['type'].value_counts())

    # Generator 초기화
    generator = SentenceGenerator(
        prompt_name='baseline_strict',
        enable_postprocessing=True  # 후처리 포함
    )

    # 교정 실행
    print(f"\n교정 진행 중... (API 호출 {len(test_df)}회)")
    corrections = []

    for idx, row in test_df.iterrows():
        err_text = row['err_sentence']

        # API 호출
        corrected = generator.generate_single(err_text)

        corrections.append({
            'index': idx,
            'type': row['type'],
            'err_sentence': err_text,
            'cor_sentence_gold': row['cor_sentence'],
            'cor_sentence_pred': corrected,
            'original_target_part': row['original_target_part'],
            'golden_target_part': row['golden_target_part']
        })

        print(f"  [{len(corrections)}/{len(test_df)}] Index {idx} ({row['type']}) 완료")

    # DataFrame 변환
    results_df = pd.DataFrame(corrections)

    # 평가
    print("\n평가 중...")

    # 정답과 예측 데이터프레임 준비
    true_df = test_df[['err_sentence', 'cor_sentence', 'original_target_part', 'golden_target_part']].reset_index(drop=True)
    pred_df = results_df[['err_sentence', 'cor_sentence_pred']].rename(columns={'cor_sentence_pred': 'cor_sentence'}).reset_index(drop=True)

    # Evaluator로 평가
    evaluator = Evaluator()
    eval_result = evaluator.evaluate(true_df, pred_df)

    # 메트릭 추출 (Evaluator는 recall/precision만 반환)
    recall = eval_result.get('recall', 0.0)
    precision = eval_result.get('precision', 0.0)

    # TP/FP/FN은 결과 데이터프레임에서 계산
    metrics = {
        'recall': recall,
        'precision': precision,
        'sample_count': len(test_df)
    }

    # 결과 출력
    print("\n" + "="*60)
    print("검증 결과")
    print("="*60)
    print(f"Recall: {recall:.2f}%")
    print(f"Precision: {precision:.2f}%")
    print(f"샘플 수: {len(test_df)}개")

    # 유형별 분석
    print("\n유형별 교정 성공 여부:")
    zero_recall_types = [
        '비문', '문장부호', '능동피동', '누락',
        '중복', '논리오류', '띄어쓰기', '외래어'
    ]

    for error_type in zero_recall_types:
        type_results = results_df[results_df['type'] == error_type]
        if len(type_results) > 0:
            # 정답과 예측이 일치하는지 확인
            matches = (type_results['cor_sentence_gold'] == type_results['cor_sentence_pred']).sum()
            print(f"  {error_type}: {matches}/{len(type_results)} 성공")

    # 결과 저장
    output_dir = Path(__file__).parent / "outputs" / "experiments"
    output_dir.mkdir(parents=True, exist_ok=True)

    # 상세 결과
    results_df.to_csv(
        output_dir / "baseline_strict_validation_20samples.csv",
        index=False,
        encoding='utf-8'
    )

    # 메트릭 결과
    with open(output_dir / "baseline_strict_validation_metrics.json", 'w', encoding='utf-8') as f:
        json.dump({
            'sample_count': len(test_df),
            'metrics': metrics,
            'selected_indices': test_indices
        }, f, ensure_ascii=False, indent=2)

    print(f"\n결과 저장 완료:")
    print(f"  - {output_dir / 'baseline_strict_validation_20samples.csv'}")
    print(f"  - {output_dir / 'baseline_strict_validation_metrics.json'}")

    return metrics, results_df


if __name__ == "__main__":
    # 재현성을 위한 시드 고정
    random.seed(42)

    metrics, results_df = validate_baseline_strict()
