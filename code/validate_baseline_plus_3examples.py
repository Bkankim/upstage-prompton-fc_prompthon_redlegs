"""
Baseline + 3 Examples Train 검증

목표:
- baseline_plus_3examples 프롬프트 검증
- RuleChecklist 후처리 사용 (안전)
- Train 254개 평가
- 목표: Recall 32-33% (기존 32.24% 유지 또는 소폭 상승)
"""

import pandas as pd
import json
import re
from pathlib import Path
from src.generator import SentenceGenerator
from src.evaluator import Evaluator


def validate_baseline_plus_3examples():
    """
    Baseline + 3 Examples Train 검증
    """
    print("="*70)
    print("Baseline + 3 Examples Train 검증")
    print("="*70)
    print()

    # 데이터 로드
    train_df = pd.read_csv(Path(__file__).parent / "data" / "train.csv")

    print(f"총 샘플: {len(train_df)}개")
    print()

    # Generator 초기화
    print("프롬프트: baseline_plus_3examples")
    print("후처리: RuleChecklist (안전)")
    print()

    generator = SentenceGenerator(
        prompt_name='baseline_plus_3examples',
        enable_postprocessing=True,
        use_enhanced_postprocessor=False  # RuleChecklist 사용
    )

    # 교정 실행
    print(f"교정 진행 중... (API 호출 {len(train_df)}회, 예상 시간: 10-15분)")
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

    # 메타데이터 체크
    def detect_metadata(text):
        if pd.isna(text):
            return False
        patterns = [r'원문:', r'교정:', r'<원문>', r'<교정>', r'\[최종', r'※', r'#']
        for pattern in patterns:
            if re.search(pattern, text):
                return True
        return False

    metadata_count = results_df['cor_sentence_pred'].apply(detect_metadata).sum()

    # 길이 폭발 체크
    results_df['length_ratio'] = results_df.apply(
        lambda row: len(row['cor_sentence_pred']) / len(row['err_sentence'])
        if len(row['err_sentence']) > 0 else 1.0,
        axis=1
    )
    length_explosion_count = len(results_df[results_df['length_ratio'] > 1.5])

    # 결과 출력
    print("\n" + "="*70)
    print("검증 결과")
    print("="*70)
    print(f"Recall: {recall:.2f}%")
    print(f"Precision: {precision:.2f}%")
    print(f"타깃 교정: {target_success}/{target_total} ({target_rate:.1f}%)")
    print(f"메타데이터: {metadata_count}개 ({metadata_count/len(train_df)*100:.1f}%)")
    print(f"길이 폭발 (>150%): {length_explosion_count}개")
    print()

    # 비교
    print("="*70)
    print("비교")
    print("="*70)
    print()
    print("기존 Baseline (검증됨):")
    print("  Train Recall: 32.24%")
    print("  Public LB: 34.04%")
    print()
    print(f"Baseline + 3 Examples:")
    print(f"  Train Recall: {recall:.2f}%")
    print(f"  차이: {recall - 32.24:+.2f}%p")
    print()

    # 판정
    print("="*70)
    print("판정")
    print("="*70)
    print()

    success = True

    if recall >= 32:
        print(f"✅ Recall {recall:.2f}% (목표: ≥32%)")
    else:
        print(f"❌ Recall {recall:.2f}% (목표: ≥32%)")
        success = False

    if metadata_count <= 10:
        print(f"✅ 메타데이터 {metadata_count}개 (목표: ≤10개)")
    else:
        print(f"⚠️ 메타데이터 {metadata_count}개 (목표: ≤10개)")

    if length_explosion_count <= 10:
        print(f"✅ 길이 폭발 {length_explosion_count}개 (목표: ≤10개)")
    else:
        print(f"⚠️ 길이 폭발 {length_explosion_count}개 (목표: ≤10개)")

    print()

    if success:
        print("🎯 검증 통과!")
        print("   → Phase 3 회귀 테스트로 진행")
    else:
        print("❌ 검증 실패")
        print("   → 프롬프트 재조정 필요")

    print()

    # 결과 저장
    output_dir = Path(__file__).parent / "outputs" / "experiments"
    output_dir.mkdir(parents=True, exist_ok=True)

    results_df.to_csv(
        output_dir / "baseline_plus_3examples_train_results.csv",
        index=False,
        encoding='utf-8'
    )

    metrics = {
        'recall': recall,
        'precision': precision,
        'target_success_rate': target_rate,
        'metadata_count': int(metadata_count),
        'length_explosion_count': length_explosion_count
    }

    with open(output_dir / "baseline_plus_3examples_train_metrics.json", 'w', encoding='utf-8') as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    print(f"결과 저장:")
    print(f"  - {output_dir / 'baseline_plus_3examples_train_results.csv'}")
    print(f"  - {output_dir / 'baseline_plus_3examples_train_metrics.json'}")
    print()

    return metrics, results_df, success


if __name__ == "__main__":
    metrics, results_df, success = validate_baseline_plus_3examples()

    if success:
        print("다음 단계: Phase 3 회귀 테스트 (62개)")
    else:
        print("다음 단계: 프롬프트 재조정")
