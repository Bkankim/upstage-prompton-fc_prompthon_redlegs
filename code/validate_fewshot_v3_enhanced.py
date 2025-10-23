"""
fewshot_v3_enhanced 프롬프트 검증 스크립트

전문가 조언 반영:
- 시드 고정 (재현성)
- 유형별 최소 2건씩 배치 (변동성 감소)
- 평가 지표 확장: Recall/Precision + 타깃 교정 + 메타데이터 + 평균 길이
- 후처리 전/후 비교 로깅
"""

import pandas as pd
import json
import random
import re
from pathlib import Path
from src.generator import SentenceGenerator
from src.evaluator import Evaluator


def select_test_samples_balanced():
    """
    검증용 20개 샘플 선정 (유형별 균형 개선)

    전문가 조언:
    - 유형별 최소 2건씩 배치 (변동성 감소)
    - Recall 0% 유형 우선 배치
    - 시드 고정 (재현성)

    Returns:
        list: 선정된 인덱스 리스트
    """
    # 데이터 로드
    train_df = pd.read_csv(Path(__file__).parent / "data" / "train.csv")

    # Recall 0% 유형 각 2개씩 선정
    zero_recall_types = [
        '비문', '문장부호', '능동피동', '누락',
        '중복', '논리오류', '띄어쓰기', '외래어'
    ]

    selected_indices = []

    # 각 유형에서 2개씩 (총 16개)
    for error_type in zero_recall_types:
        type_indices = train_df[train_df['type'] == error_type].index.tolist()
        if len(type_indices) >= 2:
            selected_indices.extend(random.sample(type_indices, 2))
        elif len(type_indices) == 1:
            selected_indices.append(type_indices[0])

    # 나머지 4개는 기타 유형에서 랜덤 선정
    remaining_indices = [
        i for i in train_df.index
        if i not in selected_indices
    ]
    selected_indices.extend(random.sample(remaining_indices, min(4, len(remaining_indices))))

    return sorted(selected_indices)


def calculate_additional_metrics(results_df):
    """
    추가 평가 지표 계산

    전문가 조언:
    - 타깃 교정 성공률
    - 메타데이터 발생률
    - 평균 길이 변화

    Args:
        results_df: 검증 결과 DataFrame

    Returns:
        dict: 추가 지표
    """
    # 타깃 교정 성공률
    def check_target_correction(row):
        golden_target = row['golden_target_part']
        pred = row['cor_sentence_pred']
        if pd.notna(golden_target) and pd.notna(pred) and golden_target in str(pred):
            return True
        return False

    target_success = results_df.apply(check_target_correction, axis=1).sum()
    target_total = results_df[results_df['golden_target_part'].notna()].shape[0]
    target_success_rate = target_success / target_total * 100 if target_total > 0 else 0

    # 메타데이터 발생률
    def detect_metadata(text):
        if pd.isna(text):
            return False
        metadata_patterns = [
            r'※', r'지시사항', r'설명', r'참고',
            r'원문:', r'교정:', r'수정:', r'결과:',
            r'<원문>', r'<교정>',
            r'\[최종', r'\[재최종', r'\[시스템',
            r'규칙.*따라', r'추가.*지시'
        ]
        for pattern in metadata_patterns:
            if re.search(pattern, text):
                return True
        return False

    metadata_count = results_df['cor_sentence_pred'].apply(detect_metadata).sum()
    metadata_rate = metadata_count / len(results_df) * 100

    # 평균 길이 변화
    def calculate_length_ratio(row):
        err_len = len(row['err_sentence'])
        pred_len = len(row['cor_sentence_pred'])
        return pred_len / err_len if err_len > 0 else 0

    length_ratios = results_df.apply(calculate_length_ratio, axis=1)
    avg_length_ratio = length_ratios.mean() * 100

    return {
        'target_success_count': int(target_success),
        'target_total_count': int(target_total),
        'target_success_rate': float(target_success_rate),
        'metadata_count': int(metadata_count),
        'metadata_rate': float(metadata_rate),
        'avg_length_ratio': float(avg_length_ratio),
    }


def validate_fewshot_v3_enhanced():
    """
    fewshot_v3_enhanced 프롬프트 검증 실행
    """
    print("="*70)
    print("fewshot_v3_enhanced + Enhanced Postprocessor 검증 시작")
    print("="*70)

    # 데이터 로드
    train_df = pd.read_csv(Path(__file__).parent / "data" / "train.csv")

    # 샘플 선정 (유형별 균형)
    test_indices = select_test_samples_balanced()
    test_df = train_df.loc[test_indices].copy()

    print(f"\n선정된 샘플: {len(test_df)}개")
    print("\n유형별 분포:")
    print(test_df['type'].value_counts())

    # Generator 초기화 (Enhanced 후처리 사용)
    generator = SentenceGenerator(
        prompt_name='fewshot_v3_enhanced',
        enable_postprocessing=True,
        use_enhanced_postprocessor=True
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

    # 메트릭 추출
    recall = eval_result.get('recall', 0.0)
    precision = eval_result.get('precision', 0.0)

    # 추가 지표 계산
    additional_metrics = calculate_additional_metrics(results_df)

    # 통합 메트릭
    metrics = {
        'recall': recall,
        'precision': precision,
        'sample_count': len(test_df),
        **additional_metrics
    }

    # 결과 출력
    print("\n" + "="*70)
    print("검증 결과")
    print("="*70)
    print(f"Recall: {recall:.2f}%")
    print(f"Precision: {precision:.2f}%")
    print(f"샘플 수: {len(test_df)}개")
    print()
    print("추가 지표:")
    print(f"  타깃 교정 성공: {additional_metrics['target_success_count']}/{additional_metrics['target_total_count']} ({additional_metrics['target_success_rate']:.1f}%)")
    print(f"  메타데이터 출현: {additional_metrics['metadata_count']}/{len(test_df)} ({additional_metrics['metadata_rate']:.1f}%)")
    print(f"  평균 길이 비율: {additional_metrics['avg_length_ratio']:.1f}%")

    # 유형별 분석
    print("\n유형별 교정 성공 여부 (Perfect Match):")
    zero_recall_types = [
        '비문', '문장부호', '능동피동', '누락',
        '중복', '논리오류', '띄어쓰기', '외래어'
    ]

    for error_type in zero_recall_types:
        type_results = results_df[results_df['type'] == error_type]
        if len(type_results) > 0:
            matches = (type_results['cor_sentence_gold'] == type_results['cor_sentence_pred']).sum()
            print(f"  {error_type}: {matches}/{len(type_results)} 성공")

    # 결과 저장
    output_dir = Path(__file__).parent / "outputs" / "experiments"
    output_dir.mkdir(parents=True, exist_ok=True)

    # 상세 결과
    results_df.to_csv(
        output_dir / "fewshot_v3_enhanced_validation_20samples.csv",
        index=False,
        encoding='utf-8'
    )

    # 메트릭 결과
    with open(output_dir / "fewshot_v3_enhanced_validation_metrics.json", 'w', encoding='utf-8') as f:
        json.dump({
            'sample_count': len(test_df),
            'metrics': metrics,
            'selected_indices': test_indices
        }, f, ensure_ascii=False, indent=2)

    # 후처리 로그 저장 (Enhanced 후처리 사용 시)
    if hasattr(generator.postprocessor, 'save_processing_log'):
        log_path = Path(__file__).parent / "outputs" / "analysis" / "fewshot_v3_enhanced_postprocess_comparison.json"
        generator.postprocessor.save_processing_log(str(log_path))
        print(f"\n후처리 로그 저장: {log_path}")

    print(f"\n결과 저장 완료:")
    print(f"  - {output_dir / 'fewshot_v3_enhanced_validation_20samples.csv'}")
    print(f"  - {output_dir / 'fewshot_v3_enhanced_validation_metrics.json'}")

    return metrics, results_df


if __name__ == "__main__":
    # 재현성을 위한 시드 고정
    random.seed(42)

    metrics, results_df = validate_fewshot_v3_enhanced()
