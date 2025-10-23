"""
Phase 5: Train 전체(254개) 평가 - Option A

목표:
- Option A (fewshot_v3 + Enhanced 후처리) 최종 성능 확정
- 취약 유형 (받침에따른, 사이시옷) 추적
- 메타데이터 발생 케이스 수동 검토
"""

import pandas as pd
import json
import re
from pathlib import Path
from src.generator import SentenceGenerator
from src.evaluator import Evaluator


def calculate_additional_metrics(results_df):
    """
    추가 평가 지표 계산
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

    # 메타데이터 발생률 (자동 탐지)
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

    # 길이 폭발 케이스 (150% 초과)
    length_explosion_cases = results_df[length_ratios > 1.5]

    return {
        'target_success_count': int(target_success),
        'target_total_count': int(target_total),
        'target_success_rate': float(target_success_rate),
        'metadata_count': int(metadata_count),
        'metadata_rate': float(metadata_rate),
        'avg_length_ratio': float(avg_length_ratio),
        'length_explosion_count': len(length_explosion_cases),
        'length_explosion_indices': length_explosion_cases['index'].tolist() if len(length_explosion_cases) > 0 else []
    }


def validate_full_train():
    """
    Train 전체(254개) 평가 실행
    """
    print("="*70)
    print("Phase 5: Train 전체(254개) Option A 최종 평가")
    print("="*70)

    # 데이터 로드
    train_df = pd.read_csv(Path(__file__).parent / "data" / "train.csv")

    print(f"\n총 샘플: {len(train_df)}개")
    print("\n유형별 분포:")
    print(train_df['type'].value_counts().sort_index())

    # Generator 초기화
    print("\n프롬프트: fewshot_v3")
    print("후처리: EnhancedPostprocessor")

    generator = SentenceGenerator(
        prompt_name='fewshot_v3',
        enable_postprocessing=True,
        use_enhanced_postprocessor=True
    )

    # 교정 실행
    print(f"\n교정 진행 중... (API 호출 {len(train_df)}회, 예상 시간: 10-15분)")
    corrections = []

    for idx, row in train_df.iterrows():
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

        # 진행 상황 출력 (매 25개마다)
        if len(corrections) % 25 == 0:
            print(f"  [{len(corrections)}/{len(train_df)}] 완료... ({len(corrections)/len(train_df)*100:.1f}%)")

    print(f"  [{len(corrections)}/{len(train_df)}] 완료! (100.0%)")

    # DataFrame 변환
    results_df = pd.DataFrame(corrections)

    # 평가
    print("\n평가 중...")

    # 정답과 예측 데이터프레임 준비
    true_df = train_df[['err_sentence', 'cor_sentence', 'original_target_part', 'golden_target_part']].reset_index(drop=True)
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
        'sample_count': len(train_df),
        **additional_metrics
    }

    # 결과 출력
    print("\n" + "="*70)
    print("Phase 5 최종 평가 결과")
    print("="*70)
    print(f"Recall: {recall:.2f}%")
    print(f"Precision: {precision:.2f}%")
    print(f"샘플 수: {len(train_df)}개")
    print()
    print("추가 지표:")
    print(f"  타깃 교정 성공: {additional_metrics['target_success_count']}/{additional_metrics['target_total_count']} ({additional_metrics['target_success_rate']:.1f}%)")
    print(f"  메타데이터 출현 (자동 탐지): {additional_metrics['metadata_count']}/{len(train_df)} ({additional_metrics['metadata_rate']:.1f}%)")
    print(f"  길이 폭발 케이스 (>150%): {additional_metrics['length_explosion_count']}개")
    print(f"  평균 길이 비율: {additional_metrics['avg_length_ratio']:.1f}%")

    # 단계별 비교
    print("\n" + "="*70)
    print("단계별 성능 비교")
    print("="*70)
    print()
    print("Phase 2 (18개 샘플):")
    print("  Recall: 42.11%")
    print("  타깃 교정: 44.4%")
    print("  메타데이터: 0.0%")
    print()
    print("Phase 3 (62개 샘플):")
    print("  Recall: 45.76%")
    print("  타깃 교정: 50.0%")
    print("  메타데이터: 1.6% (실제)")
    print()
    print(f"Phase 5 (254개 전체):")
    print(f"  Recall: {recall:.2f}%")
    print(f"  타깃 교정: {additional_metrics['target_success_rate']:.1f}%")
    print(f"  메타데이터: {additional_metrics['metadata_rate']:.1f}% (자동 탐지)")
    print()

    # 유형별 성공률 분석
    print("="*70)
    print("유형별 타깃 교정 성공률")
    print("="*70)
    print()

    type_success_rates = []
    for error_type in sorted(results_df['type'].unique()):
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
            type_success_rates.append({
                'type': error_type,
                'rate': float(type_success_rate),
                'success': int(type_target_success),
                'total': int(type_target_total)
            })
            print(f"  {error_type}: {type_target_success}/{type_target_total} ({type_success_rate:.1f}%)")

    # 취약 유형 재확인
    if type_success_rates:
        success_rates_values = [item['rate'] for item in type_success_rates]
        mean_rate = sum(success_rates_values) / len(success_rates_values)
        std_rate = (sum((r - mean_rate) ** 2 for r in success_rates_values) / len(success_rates_values)) ** 0.5
        threshold = mean_rate - std_rate

        print()
        print(f"평균 성공률: {mean_rate:.1f}%")
        print(f"표준편차: {std_rate:.1f}%")
        print(f"취약 유형 기준: < {threshold:.1f}% (평균 - 1σ)")
        print()

        weak_types = [
            item for item in type_success_rates
            if item['rate'] < threshold
        ]

        if weak_types:
            print("취약 유형:")
            for item in weak_types:
                print(f"  {item['type']}: {item['success']}/{item['total']} ({item['rate']:.1f}%)")

            # Phase 3 취약 유형과 비교
            phase3_weak = ['받침에따른', '사이시옷']
            print()
            print("Phase 3 취약 유형 추적:")
            for weak_type in phase3_weak:
                matching = [item for item in type_success_rates if item['type'] == weak_type]
                if matching:
                    item = matching[0]
                    print(f"  {item['type']}: {item['success']}/{item['total']} ({item['rate']:.1f}%)")
                    if item['rate'] < threshold:
                        print(f"    → 여전히 취약 ⚠️")
                    else:
                        print(f"    → 개선됨 ✅")
        else:
            print("취약 유형 없음 (모든 유형이 평균 - 1σ 이상)")

    print()

    # 최종 판정
    print("="*70)
    print("최종 판정")
    print("="*70)
    print()

    if recall >= 40:
        print(f"✅ Recall {recall:.2f}% 달성 (목표: ≥ 40%)")
    else:
        print(f"❌ Recall {recall:.2f}% 미달 (목표: ≥ 40%)")

    if additional_metrics['target_success_rate'] >= 45:
        print(f"✅ 타깃 교정 {additional_metrics['target_success_rate']:.1f}% 달성 (목표: ≥ 45%)")
    else:
        print(f"⚠️ 타깃 교정 {additional_metrics['target_success_rate']:.1f}% (목표: ≥ 45%)")

    if additional_metrics['metadata_rate'] <= 5:
        print(f"✅ 메타데이터 {additional_metrics['metadata_rate']:.1f}% (목표: ≤ 5%)")
    else:
        print(f"⚠️ 메타데이터 {additional_metrics['metadata_rate']:.1f}% (목표: ≤ 5%)")

    print()

    if recall >= 40 and additional_metrics['target_success_rate'] >= 45 and additional_metrics['metadata_rate'] <= 5:
        print("🎯 Option A 최종 확정!")
        print("   → Phase 6: Test LB 제출 파일 생성으로 진행")
    else:
        print("⚠️ 일부 목표 미달")
        print("   → 결과 검토 및 추가 개선 고려")

    print()

    # 결과 저장
    output_dir = Path(__file__).parent / "outputs" / "experiments"
    output_dir.mkdir(parents=True, exist_ok=True)

    # 상세 결과
    results_df.to_csv(
        output_dir / "phase5_full_train_results.csv",
        index=False,
        encoding='utf-8'
    )

    # 메트릭 결과
    with open(output_dir / "phase5_full_train_metrics.json", 'w', encoding='utf-8') as f:
        json.dump({
            'sample_count': len(train_df),
            'metrics': metrics,
            'type_success_rates': type_success_rates,
            'weak_types': weak_types if weak_types else []
        }, f, ensure_ascii=False, indent=2)

    # 메타데이터 케이스 수동 검토용
    if additional_metrics['metadata_count'] > 0:
        metadata_cases = results_df[results_df['cor_sentence_pred'].apply(
            lambda x: any(re.search(pattern, str(x)) for pattern in [
                r'※', r'지시사항', r'설명', r'참고',
                r'원문:', r'교정:', r'수정:', r'결과:',
                r'<원문>', r'<교정>',
                r'\[최종', r'\[재최종', r'\[시스템',
                r'규칙.*따라', r'추가.*지시'
            ])
        )]

        metadata_cases.to_csv(
            output_dir / "phase5_metadata_cases_for_review.csv",
            index=False,
            encoding='utf-8'
        )
        print(f"메타데이터 의심 케이스: {output_dir / 'phase5_metadata_cases_for_review.csv'}")
        print("  → 수동 검토 권장 (False Positive 확인)")
        print()

    # 후처리 로그 저장
    if hasattr(generator.postprocessor, 'save_processing_log'):
        log_path = Path(__file__).parent / "outputs" / "analysis" / "phase5_full_train_postprocess_log.json"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        generator.postprocessor.save_processing_log(str(log_path))
        print(f"후처리 로그 저장: {log_path}")

    print(f"\n결과 저장 완료:")
    print(f"  - {output_dir / 'phase5_full_train_results.csv'}")
    print(f"  - {output_dir / 'phase5_full_train_metrics.json'}")

    return metrics, results_df


if __name__ == "__main__":
    metrics, results_df = validate_full_train()
