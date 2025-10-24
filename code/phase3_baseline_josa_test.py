"""
Phase 3 회귀 테스트: Baseline + 조사 예시 1개 안정성 검증

목적:
- Baseline + 조사 예시 1개 프롬프트의 안정성 확인
- 동일한 62개 샘플로 Train 결과와 비교
- Recall 일관성 확인
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
    print('Phase 3 회귀 테스트: Baseline + 조사 예시 1개 안정성 검증')
    print('='*70)
    print()

    # Phase 3 샘플 로드
    phase3_path = Path('outputs/experiments/phase3_selected_indices.json')

    if not phase3_path.exists():
        print("⚠️ Phase 3 샘플 파일이 없습니다. Train 데이터에서 랜덤 62개 샘플링...")
        train_df = pd.read_csv('data/train.csv')
        test_indices = random.sample(range(len(train_df)), 62)

        # 저장
        phase3_path.parent.mkdir(parents=True, exist_ok=True)
        with open(phase3_path, 'w') as f:
            json.dump({'selected_indices': test_indices}, f)
        print(f"✅ Phase 3 샘플 생성 및 저장: {phase3_path}")
    else:
        with open(phase3_path, 'r') as f:
            phase3_data = json.load(f)
            test_indices = phase3_data['selected_indices']

    train_df = pd.read_csv('data/train.csv')
    test_df = train_df.loc[test_indices].copy()

    print(f'선정된 샘플: {len(test_df)}개')
    print()

    # Baseline + 조사 예시 1개 테스트
    print('프롬프트: baseline_josa (예시 없음)')
    print('후처리: RuleChecklist (안전)')
    print()

    generator = SentenceGenerator(
        prompt_name='baseline_josa',
        enable_postprocessing=True,
        use_enhanced_postprocessor=False
    )

    print(f'교정 진행 중... (API 호출 {len(test_df)}회, 예상 시간: 2-3분)')
    print()

    corrections = []
    for idx, row in test_df.iterrows():
        corrected = generator.generate_single(row['err_sentence'])
        corrections.append({
            'index': idx,
            'type': row['type'],
            'err_sentence': row['err_sentence'],
            'cor_sentence_gold': row['cor_sentence'],
            'cor_sentence_pred': corrected,
            'original_target_part': row.get('original_target_part', ''),
            'golden_target_part': row.get('golden_target_part', '')
        })
        if len(corrections) % 10 == 0:
            print(f'  [{len(corrections)}/{len(test_df)}] 완료... ({len(corrections)/len(test_df)*100:.1f}%)')

    print(f'  [{len(corrections)}/{len(test_df)}] 완료! (100.0%)')
    print()

    # 평가
    results_df = pd.DataFrame(corrections)

    true_df_data = {'err_sentence': test_df['err_sentence'].values,
                    'cor_sentence': test_df['cor_sentence'].values}

    if 'original_target_part' in test_df.columns and 'golden_target_part' in test_df.columns:
        true_df_data['original_target_part'] = test_df['original_target_part'].values
        true_df_data['golden_target_part'] = test_df['golden_target_part'].values

    true_df = pd.DataFrame(true_df_data).reset_index(drop=True)
    pred_df = results_df[['err_sentence', 'cor_sentence_pred']].rename(
        columns={'cor_sentence_pred': 'cor_sentence'}
    ).reset_index(drop=True)

    evaluator = Evaluator()
    eval_result = evaluator.evaluate(true_df, pred_df)

    recall = eval_result.get('recall', 0.0)
    precision = eval_result.get('precision', 0.0)

    # 길이 폭발 체크
    results_df['length_ratio'] = results_df.apply(
        lambda row: len(row['cor_sentence_pred']) / len(row['err_sentence'])
        if len(row['err_sentence']) > 0 else 1.0,
        axis=1
    )
    length_explosion_count = (results_df['length_ratio'] > 1.5).sum()

    # 메타데이터 체크
    import re

    def detect_metadata(text):
        if pd.isna(text):
            return False
        patterns = [r'원문:', r'교정:', r'<원문>', r'<교정>', r'\[최종', r'※', r'#']
        for pattern in patterns:
            if re.search(pattern, text):
                return True
        return False

    metadata_count = results_df['cor_sentence_pred'].apply(detect_metadata).sum()

    # 결과 출력
    print('='*70)
    print('Phase 3 회귀 테스트 결과')
    print('='*70)
    print()
    print(f'Recall:    {recall:.2f}%')
    print(f'Precision: {precision:.2f}%')
    print()

    # 비교
    print('='*70)
    print('성능 비교')
    print('='*70)
    print()
    print(f'Train 254개 (Baseline + 조사 예시 1개):   33.47%')
    print(f'Phase 3 62개 (Baseline + 조사 예시 1개):  {recall:.2f}%')
    print()

    diff = recall - 33.47
    print(f'차이: {diff:+.2f}%p')
    print()

    # 품질 체크
    print('='*70)
    print('품질 체크')
    print('='*70)
    print()
    print(f'1. 메타데이터: {metadata_count}개 ({metadata_count/len(results_df)*100:.1f}%)')
    print(f'2. 길이 폭발 (>150%): {length_explosion_count}개 ({length_explosion_count/len(results_df)*100:.1f}%)')
    print()

    # 최종 판정
    print('='*70)
    print('최종 판정')
    print('='*70)
    print()

    issues = []
    if abs(diff) > 5.0:
        issues.append(f"Train 대비 격차 큼 ({diff:+.2f}%p)")
    if recall < 30.0:
        issues.append(f"Recall 너무 낮음 ({recall:.2f}%)")
    if metadata_count > 5:
        issues.append(f"메타데이터 과다 ({metadata_count}개)")
    if length_explosion_count > 10:
        issues.append(f"길이 폭발 과다 ({length_explosion_count}개)")

    if not issues:
        print("✅ Phase 3 회귀 테스트 통과!")
        print(f"   Train과 Phase 3 일관성 확보 (차이: {diff:+.2f}%p)")
        print("   → Test 109개 생성 진행 권장")
    else:
        print("⚠️ 검토 필요 항목:")
        for issue in issues:
            print(f"   - {issue}")
        print("   → 프롬프트 조정 또는 재검증 필요")
    print()

    # 결과 저장
    output_dir = Path('outputs/logs')
    output_dir.mkdir(parents=True, exist_ok=True)

    log_data = {
        'prompt': 'baseline_josa',
        'dataset': 'phase3',
        'samples': len(results_df),
        'recall': recall,
        'precision': precision,
        'train_recall': 33.47,
        'diff': diff,
        'quality_checks': {
            'metadata_count': int(metadata_count),
            'length_explosion_count': int(length_explosion_count)
        }
    }

    log_path = output_dir / 'baseline_josa_phase3_results.json'
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, ensure_ascii=False, indent=2)

    print(f'로그 저장: {log_path}')
    print()

    # CSV 저장
    csv_path = output_dir / 'baseline_josa_phase3_results.csv'
    results_df.to_csv(csv_path, index=False, encoding='utf-8')
    print(f'결과 저장: {csv_path}')
    print()


if __name__ == "__main__":
    main()
