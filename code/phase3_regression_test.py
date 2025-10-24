"""
Phase 3 회귀 테스트: 개선 효과 검증

목적:
- 후처리 보완 + 프롬프트 개선 효과 확인
- 동일한 62개 샘플로 직접 비교
"""

import pandas as pd
import json
import random
from pathlib import Path
from src.generator import SentenceGenerator
from src.evaluator import Evaluator


def main():
    # 시드 고정
    random.seed(42)

    print('='*70)
    print('Phase 3 회귀 테스트: 개선 효과 검증')
    print('='*70)
    print()

    # Phase 3 샘플 로드
    with open('outputs/experiments/phase3_selected_indices.json', 'r') as f:
        phase3_data = json.load(f)
        test_indices = phase3_data['selected_indices']

    train_df = pd.read_csv('data/train.csv')
    test_df = train_df.loc[test_indices].copy()

    print(f'선정된 샘플: {len(test_df)}개 (기존 Phase 3와 동일)')
    print()

    # 개선된 Option A 테스트
    print('프롬프트: baseline_plus_3examples')
    print('후처리: RuleChecklist (안전)')
    print()

    generator = SentenceGenerator(
        prompt_name='baseline_plus_3examples',
        enable_postprocessing=True,
        use_enhanced_postprocessor=False
    )

    print(f'교정 진행 중... (API 호출 {len(test_df)}회)')

    corrections = []
    for idx, row in test_df.iterrows():
        corrected = generator.generate_single(row['err_sentence'])
        corrections.append({
            'index': idx,
            'type': row['type'],
            'err_sentence': row['err_sentence'],
            'cor_sentence_gold': row['cor_sentence'],
            'cor_sentence_pred': corrected,
            'original_target_part': row['original_target_part'],
            'golden_target_part': row['golden_target_part']
        })
        if len(corrections) % 10 == 0:
            print(f'  [{len(corrections)}/{len(test_df)}] 완료...')

    print(f'  [{len(corrections)}/{len(test_df)}] 완료!')
    print()

    # 평가
    results_df = pd.DataFrame(corrections)

    true_df = test_df[['err_sentence', 'cor_sentence', 'original_target_part', 'golden_target_part']].reset_index(drop=True)
    pred_df = results_df[['err_sentence', 'cor_sentence_pred']].rename(columns={'cor_sentence_pred': 'cor_sentence'}).reset_index(drop=True)

    evaluator = Evaluator()
    eval_result = evaluator.evaluate(true_df, pred_df)

    recall = eval_result.get('recall', 0.0)
    precision = eval_result.get('precision', 0.0)

    # 추가 지표
    def calc_target_rate():
        def check_target(row):
            golden = row['golden_target_part']
            pred = row['cor_sentence_pred']
            if pd.notna(golden) and pd.notna(pred) and golden in str(pred):
                return True
            return False

        success = results_df.apply(check_target, axis=1).sum()
        total = results_df[results_df['golden_target_part'].notna()].shape[0]
        rate = success / total * 100 if total > 0 else 0
        return success, total, rate

    target_success, target_total, target_rate = calc_target_rate()

    # 길이 폭발 체크
    results_df['length_ratio'] = results_df.apply(
        lambda row: len(row['cor_sentence_pred']) / len(row['err_sentence'])
        if len(row['err_sentence']) > 0 else 1.0,
        axis=1
    )
    length_explosion_count = len(results_df[results_df['length_ratio'] > 1.5])

    # 결과 출력
    print('='*70)
    print('회귀 테스트 결과')
    print('='*70)
    print(f'Recall: {recall:.2f}%')
    print(f'Precision: {precision:.2f}%')
    print(f'타깃 교정: {target_success}/{target_total} ({target_rate:.1f}%)')
    print(f'길이 폭발 (>150%): {length_explosion_count}개')
    print()

    print('='*70)
    print('비교 (기존 Phase 3 vs 개선 Phase 3)')
    print('='*70)
    print(f'Recall:      45.76% → {recall:.2f}% ({recall - 45.76:+.2f}%p)')
    print(f'타깃 교정:   50.0%  → {target_rate:.1f}% ({target_rate - 50.0:+.1f}%p)')
    print(f'길이 폭발:   미측정  → {length_explosion_count}개')
    print()

    # 판정
    if recall >= 45 and target_rate >= 50:
        print('✅ 회귀 테스트 성공!')
        print('   → 성능 유지 또는 개선 확인')
        print('   → Phase 5 재평가로 진행 가능')
    elif recall >= 40:
        print('⚠️ 회귀 테스트 부분 성공')
        print('   → Recall은 양호하나 타깃 교정 검토 필요')
    else:
        print('❌ 회귀 테스트 실패')
        print('   → 추가 개선 필요')

    print()

    # 결과 저장
    results_df.to_csv('outputs/experiments/phase3_regression_test_results.csv', index=False)
    print('결과 저장: outputs/experiments/phase3_regression_test_results.csv')


if __name__ == '__main__':
    main()
