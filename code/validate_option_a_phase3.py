"""
Phase 3 확대 검증: Option A (fewshot_v3 + Enhanced 후처리)

목표:
- 62개 샘플로 Option A 안정성 검증
- 타깃 교정률 안정성 확인
- 동일한 로깅 구조 유지 (전문가 조언)
"""

import pandas as pd
import json
import re
from pathlib import Path
from src.generator import SentenceGenerator
from src.evaluator import Evaluator


def load_phase3_samples():
    """
    Phase 3 선정 샘플 로드
    """
    # 선정 인덱스 로드
    with open(Path(__file__).parent / "outputs" / "experiments" / "phase3_selected_indices.json", 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data['selected_indices']


def calculate_additional_metrics(results_df):
    """
    추가 평가 지표 계산 (18개 검증과 동일)
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


def validate_option_a_phase3():
    """
    Phase 3 확대 검증 실행: Option A (fewshot_v3 + Enhanced 후처리)
    """
    print("="*70)
    print("Phase 3 확대 검증: Option A (fewshot_v3 + Enhanced 후처리)")
    print("="*70)

    # 데이터 로드
    train_df = pd.read_csv(Path(__file__).parent / "data" / "train.csv")

    # Phase 3 샘플 로드
    test_indices = load_phase3_samples()
    test_df = train_df.loc[test_indices].copy()

    print(f"\n선정된 샘플: {len(test_df)}개")
    print("\n유형별 분포:")
    print(test_df['type'].value_counts().sort_index())

    # Generator 초기화 (Option A: fewshot_v3 + Enhanced 후처리)
    print("\n프롬프트: fewshot_v3 (원본)")
    print("후처리: EnhancedPostprocessor (메타데이터 제거 강화)")

    generator = SentenceGenerator(
        prompt_name='fewshot_v3',
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

        # 진행 상황 출력 (매 10개마다)
        if len(corrections) % 10 == 0:
            print(f"  [{len(corrections)}/{len(test_df)}] 완료...")

    print(f"  [{len(corrections)}/{len(test_df)}] 완료!")

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
    print("Phase 3 확대 검증 결과")
    print("="*70)
    print(f"Recall: {recall:.2f}%")
    print(f"Precision: {precision:.2f}%")
    print(f"샘플 수: {len(test_df)}개")
    print()
    print("추가 지표:")
    print(f"  타깃 교정 성공: {additional_metrics['target_success_count']}/{additional_metrics['target_total_count']} ({additional_metrics['target_success_rate']:.1f}%)")
    print(f"  메타데이터 출현: {additional_metrics['metadata_count']}/{len(test_df)} ({additional_metrics['metadata_rate']:.1f}%)")
    print(f"  평균 길이 비율: {additional_metrics['avg_length_ratio']:.1f}%")

    # 비교 기준 출력
    print("\n" + "="*70)
    print("비교 기준")
    print("="*70)
    print()
    print("Phase 2 검증 (18개 샘플):")
    print("  Recall: 42.11%")
    print("  타깃 교정: 44.4%")
    print("  메타데이터: 0.0%")
    print()
    print("Phase 3 확대 검증 (62개 샘플):")
    print(f"  Recall: {recall:.2f}%")
    print(f"  타깃 교정: {additional_metrics['target_success_rate']:.1f}%")
    print(f"  메타데이터: {additional_metrics['metadata_rate']:.1f}%")
    print()

    # 유형별 성공률 분석
    print("유형별 타깃 교정 성공률:")
    type_success_rates = []
    for error_type in results_df['type'].unique():
        type_results = results_df[results_df['type'] == error_type]
        type_target_total = type_results[type_results['golden_target_part'].notna()].shape[0]

        if type_target_total > 0:
            type_target_success = type_results.apply(
                lambda row: pd.notna(row['golden_target_part']) and
                            pd.notna(row['cor_sentence_pred']) and
                            row['golden_target_part'] in str(row['cor_sentence_pred']),
                axis=1
            ).sum()
            type_success_rate = type_target_success / type_target_total * 100
            type_success_rates.append((error_type, type_success_rate, type_target_success, type_target_total))
            print(f"  {error_type}: {type_target_success}/{type_target_total} ({type_success_rate:.1f}%)")

    # 취약 유형 식별 (성공률 평균 - 1σ 이하)
    if type_success_rates:
        success_rates = [rate for _, rate, _, _ in type_success_rates]
        mean_rate = sum(success_rates) / len(success_rates)
        std_rate = (sum((r - mean_rate) ** 2 for r in success_rates) / len(success_rates)) ** 0.5
        threshold = mean_rate - std_rate

        print()
        print(f"평균 성공률: {mean_rate:.1f}%")
        print(f"표준편차: {std_rate:.1f}%")
        print(f"취약 유형 기준: < {threshold:.1f}% (평균 - 1σ)")
        print()

        weak_types = [
            (error_type, rate, success, total)
            for error_type, rate, success, total in type_success_rates
            if rate < threshold
        ]

        if weak_types:
            print("취약 유형:")
            for error_type, rate, success, total in weak_types:
                print(f"  {error_type}: {success}/{total} ({rate:.1f}%)")
        else:
            print("취약 유형 없음 (모든 유형이 평균 - 1σ 이상)")

    print()

    # 판단
    print("="*70)
    print("검증 판정")
    print("="*70)
    print()

    if recall >= 40 and additional_metrics['metadata_rate'] == 0:
        print("✅ Phase 3 확대 검증 성공!")
        print(f"   → Recall {recall:.2f}% 유지 (40% 이상)")
        print("   → 메타데이터 0% 유지")

        if additional_metrics['target_success_rate'] >= 50:
            print(f"   → 타깃 교정률 {additional_metrics['target_success_rate']:.1f}% (50% 이상)")
            print()
            print("🎯 Option A 최종 확정 권장!")
            print("   → Phase 5: Train 전체(254개) 평가로 진행")
        else:
            print(f"   ⚠️ 타깃 교정률 {additional_metrics['target_success_rate']:.1f}% (50% 미만)")
            print()
            print("🔄 Option B 병행 검토 권장")
            print("   → fewshot_v3_enhanced_v2 (레이블 제거, System 메시지)")
    else:
        print("❌ Phase 3 확대 검증 실패")
        if recall < 40:
            print(f"   → Recall {recall:.2f}% (40% 미만)")
        if additional_metrics['metadata_rate'] > 0:
            print(f"   → 메타데이터 {additional_metrics['metadata_rate']:.1f}% 발생")
        print()
        print("🔄 Option B 실험 필수")

    print()

    # 결과 저장
    output_dir = Path(__file__).parent / "outputs" / "experiments"
    output_dir.mkdir(parents=True, exist_ok=True)

    # 상세 결과
    results_df.to_csv(
        output_dir / "phase3_option_a_results.csv",
        index=False,
        encoding='utf-8'
    )

    # 메트릭 결과 (int64 → int 변환)
    with open(output_dir / "phase3_option_a_metrics.json", 'w', encoding='utf-8') as f:
        json.dump({
            'sample_count': len(test_df),
            'metrics': metrics,
            'type_success_rates': [
                {'type': t, 'rate': float(r), 'success': int(s), 'total': int(total)}
                for t, r, s, total in type_success_rates
            ] if type_success_rates else [],
            'selected_indices': [int(idx) for idx in test_indices]
        }, f, ensure_ascii=False, indent=2)

    # 후처리 로그 저장
    if hasattr(generator.postprocessor, 'save_processing_log'):
        log_path = Path(__file__).parent / "outputs" / "analysis" / "phase3_option_a_postprocess_comparison.json"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        generator.postprocessor.save_processing_log(str(log_path))
        print(f"후처리 로그 저장: {log_path}")

    print(f"\n결과 저장 완료:")
    print(f"  - {output_dir / 'phase3_option_a_results.csv'}")
    print(f"  - {output_dir / 'phase3_option_a_metrics.json'}")

    return metrics, results_df


if __name__ == "__main__":
    metrics, results_df = validate_option_a_phase3()
