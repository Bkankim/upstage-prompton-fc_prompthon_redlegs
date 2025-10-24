"""
Baseline + EnhancedPostprocessor 검증

목표:
- 검증된 Baseline 프롬프트 + 개선된 후처리
- Train 254개 재평가
- Recall 34%+ 확인 후 Test 생성
"""

import pandas as pd
import json
from pathlib import Path
from src.generator import SentenceGenerator
from src.evaluator import Evaluator


def validate_baseline_enhanced():
    """
    Baseline + EnhancedPostprocessor 검증
    """
    print("="*70)
    print("Baseline + EnhancedPostprocessor 검증")
    print("="*70)
    print()

    # 데이터 로드
    train_df = pd.read_csv(Path(__file__).parent / "data" / "train.csv")

    print(f"총 샘플: {len(train_df)}개")
    print()

    # Generator 초기화
    print("프롬프트: baseline (검증됨)")
    print("후처리: EnhancedPostprocessor (개선판)")
    print()

    generator = SentenceGenerator(
        prompt_name='baseline',
        enable_postprocessing=True,
        use_enhanced_postprocessor=True
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

    # 길이 폭발 체크
    results_df['length_ratio'] = results_df.apply(
        lambda row: len(row['cor_sentence_pred']) / len(row['err_sentence'])
        if len(row['err_sentence']) > 0 else 1.0,
        axis=1
    )
    length_explosion_count = len(results_df[results_df['length_ratio'] > 1.5])

    # 메타데이터 체크
    import re
    def detect_metadata(text):
        if pd.isna(text):
            return False
        metadata_patterns = [
            r'※', r'지시사항', r'설명', r'참고',
            r'원문:', r'교정:', r'수정:', r'결과:',
            r'<원문>', r'<교정>',
            r'\[최종', r'\[재최종', r'\[시스템'
        ]
        for pattern in metadata_patterns:
            if re.search(pattern, text):
                return True
        return False

    metadata_count = results_df['cor_sentence_pred'].apply(detect_metadata).sum()

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
    print("기존 최고 (Baseline + RuleChecklist):")
    print("  Train Recall: 32.24%")
    print("  Public LB: 34.04%")
    print("  Private LB: 13.45%")
    print()
    print(f"개선 버전 (Baseline + EnhancedPostprocessor):")
    print(f"  Train Recall: {recall:.2f}%")
    print(f"  메타데이터: {metadata_count}개 (기존: 미측정)")
    print(f"  길이 폭발: {length_explosion_count}개 (기존: 미측정)")
    print()

    # 판정
    print("="*70)
    print("판정")
    print("="*70)
    print()

    if recall >= 32:
        print(f"✅ Recall {recall:.2f}% (기존 32.24% 이상)")
        if recall > 32.24:
            print(f"   → 개선 효과 확인 (+{recall - 32.24:.2f}%p)")
            print(f"   → Test 생성 및 LB 제출 권장")
        else:
            print(f"   → 유사한 성능, 안정성 확보")
            print(f"   → Test 생성 가능 (신중)")
    else:
        print(f"❌ Recall {recall:.2f}% (기존 32.24% 미만)")
        print(f"   → 성능 하락 (-{32.24 - recall:.2f}%p)")
        print(f"   → 재조정 필요 또는 기존 파일 사용")

    print()

    # 결과 저장
    output_dir = Path(__file__).parent / "outputs" / "experiments"
    output_dir.mkdir(parents=True, exist_ok=True)

    results_df.to_csv(
        output_dir / "baseline_enhanced_validation.csv",
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

    with open(output_dir / "baseline_enhanced_metrics.json", 'w', encoding='utf-8') as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    print(f"결과 저장:")
    print(f"  - {output_dir / 'baseline_enhanced_validation.csv'}")
    print(f"  - {output_dir / 'baseline_enhanced_metrics.json'}")
    print()

    # 후처리 로그 저장
    if hasattr(generator.postprocessor, 'save_processing_log'):
        log_path = Path(__file__).parent / "outputs" / "analysis" / "baseline_enhanced_postprocess_log.json"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        generator.postprocessor.save_processing_log(str(log_path))
        print(f"  - {log_path}")

    print()

    return metrics, results_df, recall >= 32


if __name__ == "__main__":
    metrics, results_df, should_proceed = validate_baseline_enhanced()

    if should_proceed:
        print("다음 단계: Test 109개 생성 및 LB 제출")
    else:
        print("다음 단계: 기존 최고 파일 재제출 (submission_baseline_test_clean.csv)")
