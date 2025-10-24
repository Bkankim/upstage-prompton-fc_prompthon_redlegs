"""
Baseline + 조사 예시 1개 Train 검증

목표:
- Baseline + 조사 예시 1개 프롬프트 성능 측정
- Train 254개 샘플로 Recall/Precision 계산
- Baseline(32.24%), Plus3(34.69%)와 비교
"""

import pandas as pd
import json
from pathlib import Path
from src.generator import SentenceGenerator
from src.evaluator import Evaluator


def validate_baseline_josa():
    """
    Baseline + 조사 예시 1개 Train 검증
    """
    print("="*70)
    print("Baseline + 조사 예시 1개 Train 검증")
    print("="*70)
    print()

    # Train 데이터 로드
    train_df = pd.read_csv(Path(__file__).parent / "data" / "train.csv")

    print(f"Train 샘플: {len(train_df)}개")
    print()

    # Generator 초기화
    print("프롬프트: baseline_josa (예시 없음)")
    print("후처리: RuleChecklist (안전)")
    print()

    generator = SentenceGenerator(
        prompt_name='baseline_josa',
        enable_postprocessing=True,
        use_enhanced_postprocessor=False  # RuleChecklist만 사용
    )

    # 교정 실행
    print(f"교정 진행 중... (API 호출 {len(train_df)}회, 예상 시간: 10-15분)")
    print()

    corrections = []
    for idx, row in train_df.iterrows():
        err_text = row['err_sentence']
        cor_text = row['cor_sentence']

        # API 호출
        predicted = generator.generate_single(err_text)

        corrections.append({
            'index': idx,
            'type': row['type'],
            'err_sentence': err_text,
            'cor_sentence_gold': cor_text,
            'cor_sentence_pred': predicted
        })

        # 진행 상황 출력
        if len(corrections) % 50 == 0:
            print(f"  [{len(corrections)}/{len(train_df)}] 완료... ({len(corrections)/len(train_df)*100:.1f}%)")

    print(f"  [{len(corrections)}/{len(train_df)}] 완료! (100.0%)")
    print()

    # DataFrame 변환
    results_df = pd.DataFrame(corrections)

    # Recall/Precision 계산
    print("="*70)
    print("Recall/Precision 계산")
    print("="*70)
    print()

    # Evaluator 사용
    evaluator = Evaluator()

    # true_df 준비
    true_df = pd.DataFrame({
        'err_sentence': results_df['err_sentence'],
        'cor_sentence': results_df['cor_sentence_gold']
    })

    # pred_df 준비
    pred_df = pd.DataFrame({
        'err_sentence': results_df['err_sentence'],
        'cor_sentence': results_df['cor_sentence_pred']
    })

    eval_results = evaluator.evaluate(true_df, pred_df)

    recall = eval_results['recall']
    precision = eval_results['precision']
    tp = eval_results['true_positives']
    fp = eval_results['false_positives']
    fm = eval_results['false_missings']
    fr = eval_results['false_redundants']

    print(f"Recall:    {recall:.2f}%")
    print(f"Precision: {precision:.2f}%")
    print(f"TP: {tp}, FP: {fp}, FM: {fm}, FR: {fr}")
    print()

    # 오류 유형별 분석
    print("="*70)
    print("오류 유형별 성능")
    print("="*70)
    print()

    type_metrics = {}
    for error_type in results_df['type'].unique():
        type_indices = results_df['type'] == error_type
        type_true_df = true_df[type_indices].reset_index(drop=True)
        type_pred_df = pred_df[type_indices].reset_index(drop=True)

        type_result = evaluator.evaluate(type_true_df, type_pred_df)
        type_metrics[error_type] = type_result

        print(f"{error_type:15s}: Recall {type_result['recall']:6.2f}%, "
              f"Precision {type_result['precision']:6.2f}%, "
              f"샘플 {len(type_true_df):3d}개")

    print()

    # 비교
    print("="*70)
    print("성능 비교")
    print("="*70)
    print()
    print(f"Baseline (1개 예시):      32.24%")
    print(f"Plus3 (4개 예시):         34.69%")
    print(f"Baseline + 조사 예시 1개:    {recall:.2f}%")
    print()

    # 메타데이터 체크
    print("="*70)
    print("품질 체크")
    print("="*70)
    print()

    # 1. 메타데이터 탐지
    import re

    def detect_metadata(text):
        if pd.isna(text):
            return False
        patterns = [r'원문:', r'교정:', r'<원문>', r'<교정>', r'\[최종', r'※', r'#']
        for pattern in patterns:
            if re.search(pattern, text):
                return True
        return False

    metadata_mask = results_df['cor_sentence_pred'].apply(detect_metadata)
    metadata_count = metadata_mask.sum()

    print(f"1. 메타데이터 탐지: {metadata_count}개 ({metadata_count/len(results_df)*100:.1f}%)")
    if metadata_count > 0:
        print(f"   ⚠️ 메타데이터 케이스:")
        for idx in results_df[metadata_mask].index[:5]:
            row = results_df.loc[idx]
            print(f"   - Index {row['index']}: {row['cor_sentence_pred'][:50]}...")
    else:
        print(f"   ✅ 메타데이터 없음")
    print()

    # 2. 길이 폭발 체크
    results_df['length_ratio'] = results_df.apply(
        lambda row: len(row['cor_sentence_pred']) / len(row['err_sentence'])
        if len(row['err_sentence']) > 0 else 1.0,
        axis=1
    )
    length_explosion_mask = results_df['length_ratio'] > 1.5
    length_explosion_count = length_explosion_mask.sum()

    print(f"2. 길이 폭발 (>150%): {length_explosion_count}개 ({length_explosion_count/len(results_df)*100:.1f}%)")
    if length_explosion_count > 0:
        print(f"   ⚠️ 길이 폭발 케이스:")
        for idx in results_df[length_explosion_mask].index[:5]:
            row = results_df.loc[idx]
            print(f"   - Index {row['index']}: {row['length_ratio']:.1%} ({len(row['err_sentence'])}자 → {len(row['cor_sentence_pred'])}자)")
    else:
        print(f"   ✅ 길이 폭발 없음")
    print()

    # 3. 길이 극단 감소 체크
    extreme_short_mask = results_df['length_ratio'] < 0.5
    extreme_short_count = extreme_short_mask.sum()

    print(f"3. 길이 극단 감소 (<50%): {extreme_short_count}개 ({extreme_short_count/len(results_df)*100:.1f}%)")
    if extreme_short_count > 0:
        print(f"   ⚠️ 극단 감소 케이스:")
        for idx in results_df[extreme_short_mask].index[:5]:
            row = results_df.loc[idx]
            print(f"   - Index {row['index']}: {row['length_ratio']:.1%} ({len(row['err_sentence'])}자 → {len(row['cor_sentence_pred'])}자)")
    else:
        print(f"   ✅ 극단 감소 없음")
    print()

    # 결과 저장
    output_dir = Path(__file__).parent / "outputs" / "logs"
    output_dir.mkdir(parents=True, exist_ok=True)

    # JSON 로그
    log_data = {
        'prompt': 'baseline_josa',
        'dataset': 'train',
        'samples': len(results_df),
        'metrics': {
            'recall': recall,
            'precision': precision,
            'true_positives': tp,
            'false_positives': fp,
            'false_missings': fm,
            'false_redundants': fr
        },
        'type_metrics': {k: {'recall': v['recall'], 'precision': v['precision'],
                             'true_positives': v['true_positives'],
                             'false_positives': v['false_positives'],
                             'false_missings': v['false_missings'],
                             'false_redundants': v['false_redundants']}
                        for k, v in type_metrics.items()},
        'quality_checks': {
            'metadata_count': int(metadata_count),
            'length_explosion_count': int(length_explosion_count),
            'extreme_short_count': int(extreme_short_count)
        }
    }

    log_path = output_dir / "baseline_josa_train_results.json"
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, ensure_ascii=False, indent=2)

    print(f"로그 저장: {log_path}")
    print()

    # CSV 저장
    csv_path = output_dir / "baseline_josa_train_results.csv"
    results_df.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"결과 저장: {csv_path}")
    print()

    # 최종 판정
    print("="*70)
    print("최종 판정")
    print("="*70)
    print()

    issues = []
    if metadata_count > 10:
        issues.append(f"메타데이터 과다 ({metadata_count}개)")
    if length_explosion_count > 20:
        issues.append(f"길이 폭발 과다 ({length_explosion_count}개)")
    if extreme_short_count > 5:
        issues.append(f"극단 감소 과다 ({extreme_short_count}개)")

    if recall < 30.0:
        issues.append(f"Recall 너무 낮음 ({recall:.2f}%)")

    if not issues:
        print("✅ Train 검증 통과!")
        print(f"   Recall: {recall:.2f}% (목표: 32-35%)")
        print("   → Phase 3 회귀 테스트 진행 권장")
    else:
        print("⚠️ 검토 필요 항목:")
        for issue in issues:
            print(f"   - {issue}")
        print("   → 프롬프트 조정 또는 후처리 강화 필요")
    print()

    return results_df, eval_results


if __name__ == "__main__":
    results_df, metrics = validate_baseline_josa()
