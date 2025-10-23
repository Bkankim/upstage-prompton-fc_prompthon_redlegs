"""
Few-shot v3 실패 원인 심층 분석 스크립트

검증 결과를 다각도로 분석:
1. 타겟 오류 교정 성공률
2. 부수적 변경 (과교정) 발생률
3. 메타데이터 출현 빈도
4. 텍스트 반복 발생
5. 길이 변화 패턴
"""

import pandas as pd
import re
from pathlib import Path


def analyze_target_correction(row):
    """
    타겟 오류 부분이 정확히 교정되었는지 확인

    Returns:
        bool: 타겟 교정 성공 여부
    """
    gold_target = row['golden_target_part']
    pred = row['cor_sentence_pred']

    # 정답 타겟이 예측에 포함되어 있는가?
    if pd.notna(gold_target) and gold_target in pred:
        return True
    return False


def detect_metadata(text):
    """
    메타데이터 출현 탐지

    Returns:
        dict: 메타데이터 정보
    """
    metadata_patterns = [
        r'※',
        r'지시사항',
        r'설명 없이',
        r'교정문만',
        r'<원문>',
        r'<교정>',
        r'원문:',
        r'교정:',
        r'오류 유형',
        r'---',
        r'###'
    ]

    detected = []
    for pattern in metadata_patterns:
        if re.search(pattern, text):
            detected.append(pattern)

    return {
        'has_metadata': len(detected) > 0,
        'patterns': detected,
        'metadata_text': [m for m in re.findall(r'※.*', text)]
    }


def detect_repetition(text):
    """
    텍스트 반복 탐지

    Returns:
        dict: 반복 정보
    """
    # 문장을 마침표 기준으로 분리
    sentences = [s.strip() for s in re.split(r'[.!?]', text) if s.strip()]

    # 중복 문장 찾기
    unique_sentences = set(sentences)
    repetition_count = len(sentences) - len(unique_sentences)

    return {
        'total_sentences': len(sentences),
        'unique_sentences': len(unique_sentences),
        'repeated_sentences': repetition_count,
        'repetition_ratio': repetition_count / len(sentences) if sentences else 0
    }


def analyze_length_change(row):
    """
    텍스트 길이 변화 분석

    Returns:
        dict: 길이 변화 정보
    """
    err_len = len(row['err_sentence'])
    gold_len = len(row['cor_sentence_gold'])
    pred_len = len(row['cor_sentence_pred'])

    gold_change = (gold_len - err_len) / err_len if err_len > 0 else 0
    pred_change = (pred_len - err_len) / err_len if err_len > 0 else 0

    return {
        'err_len': err_len,
        'gold_len': gold_len,
        'pred_len': pred_len,
        'gold_change_pct': gold_change * 100,
        'pred_change_pct': pred_change * 100,
        'excessive_expansion': pred_len > err_len * 1.5  # 150% 이상 증가
    }


def count_character_differences(gold, pred):
    """
    정답과 예측 간 문자 차이 개수 계산

    Returns:
        int: 다른 문자 수
    """
    # 간단한 문자 단위 비교
    diff_count = 0
    max_len = max(len(gold), len(pred))

    for i in range(max_len):
        gold_char = gold[i] if i < len(gold) else ''
        pred_char = pred[i] if i < len(pred) else ''
        if gold_char != pred_char:
            diff_count += 1

    return diff_count


def analyze_fewshot_failure():
    """
    Few-shot 실패 원인 심층 분석
    """
    print("="*80)
    print("Few-shot v3 실패 원인 심층 분석")
    print("="*80)

    # 데이터 로드
    results_path = Path(__file__).parent / "outputs" / "experiments" / "fewshot_v3_validation_20samples.csv"
    df = pd.read_csv(results_path)

    print(f"\n총 샘플 수: {len(df)}개\n")

    # 1. 타겟 오류 교정 성공률
    print("="*80)
    print("1. 타겟 오류 교정 성공률 분석")
    print("="*80)

    zero_recall_types = ['비문', '문장부호', '능동피동', '누락', '중복', '논리오류', '띄어쓰기', '외래어']

    target_success_count = 0
    for idx, row in df.iterrows():
        if row['type'] in zero_recall_types:
            if analyze_target_correction(row):
                target_success_count += 1
                print(f"\n✅ [{row['type']}] Index {row['index']}: 타겟 교정 성공!")
                print(f"   타겟 오류: {row['original_target_part']} → {row['golden_target_part']}")
                print(f"   예측에 포함: '{row['golden_target_part']}' in 예측")

    zero_recall_samples = len(df[df['type'].isin(zero_recall_types)])
    print(f"\n타겟 교정 성공률: {target_success_count}/{zero_recall_samples} ({target_success_count/zero_recall_samples*100:.1f}%)")

    # 2. 부수적 변경 (과교정) 분석
    print("\n" + "="*80)
    print("2. 부수적 변경 (과교정) 분석")
    print("="*80)

    for idx, row in df.iterrows():
        if row['type'] in zero_recall_types:
            gold = row['cor_sentence_gold']
            pred = row['cor_sentence_pred']

            if gold != pred:
                diff_count = count_character_differences(gold, pred)
                print(f"\n[{row['type']}] Index {row['index']}")
                print(f"  문자 차이: {diff_count}자")

                # 샘플 차이 표시 (처음 200자만)
                if len(gold) < 200:
                    print(f"  정답: {gold[:200]}")
                    print(f"  예측: {pred[:200]}")

    # 3. 메타데이터 출현 분석
    print("\n" + "="*80)
    print("3. 메타데이터 출현 분석")
    print("="*80)

    metadata_count = 0
    for idx, row in df.iterrows():
        metadata_info = detect_metadata(row['cor_sentence_pred'])
        if metadata_info['has_metadata']:
            metadata_count += 1
            print(f"\n❌ Index {row['index']} ({row['type']}): 메타데이터 발견!")
            print(f"   패턴: {metadata_info['patterns']}")
            if metadata_info['metadata_text']:
                print(f"   내용: {metadata_info['metadata_text']}")

    print(f"\n메타데이터 출현: {metadata_count}/{len(df)} ({metadata_count/len(df)*100:.1f}%)")

    # 4. 텍스트 반복 분석
    print("\n" + "="*80)
    print("4. 텍스트 반복 분석")
    print("="*80)

    repetition_count = 0
    for idx, row in df.iterrows():
        rep_info = detect_repetition(row['cor_sentence_pred'])
        if rep_info['repeated_sentences'] > 0:
            repetition_count += 1
            print(f"\n❌ Index {row['index']} ({row['type']}): 문장 반복 발견!")
            print(f"   전체 문장: {rep_info['total_sentences']}개")
            print(f"   고유 문장: {rep_info['unique_sentences']}개")
            print(f"   반복 문장: {rep_info['repeated_sentences']}개")
            print(f"   반복 비율: {rep_info['repetition_ratio']*100:.1f}%")

    print(f"\n반복 출현: {repetition_count}/{len(df)} ({repetition_count/len(df)*100:.1f}%)")

    # 5. 길이 변화 분석
    print("\n" + "="*80)
    print("5. 길이 변화 분석")
    print("="*80)

    excessive_expansion_count = 0
    for idx, row in df.iterrows():
        len_info = analyze_length_change(row)
        if len_info['excessive_expansion']:
            excessive_expansion_count += 1
            print(f"\n⚠️  Index {row['index']} ({row['type']}): 과도한 길이 증가!")
            print(f"   원문: {len_info['err_len']}자")
            print(f"   정답: {len_info['gold_len']}자 ({len_info['gold_change_pct']:+.1f}%)")
            print(f"   예측: {len_info['pred_len']}자 ({len_info['pred_change_pct']:+.1f}%)")

    print(f"\n과도한 확장: {excessive_expansion_count}/{len(df)} ({excessive_expansion_count/len(df)*100:.1f}%)")

    # 6. 종합 결론
    print("\n" + "="*80)
    print("6. 종합 결론")
    print("="*80)

    print(f"""
Few-shot v3가 실패한 핵심 원인:

1. 타겟 교정은 성공했다! ({target_success_count}/{zero_recall_samples} = {target_success_count/zero_recall_samples*100:.1f}%)
   → Few-shot 학습 자체는 작동함
   → "부딪혀", "매뉴얼", "원수지간" 등 정확히 교정

2. 부수적 변경 (과교정) 문제
   → 타겟 오류 외 다른 부분도 수정
   → 예: "10만명" → "10만 명" (띄어쓰기 추가)
   → 예: "대신해서" → "대신해" (불필요한 축약)

3. 메타데이터 출현 ({metadata_count}/{len(df)} = {metadata_count/len(df)*100:.1f}%)
   → "※ 지시사항에 따라..." 같은 설명 추가
   → 후처리가 이를 제거하지 못함

4. 텍스트 반복 ({repetition_count}/{len(df)} = {repetition_count/len(df)*100:.1f}%)
   → 같은 문장을 2~3번 반복 출력
   → 길이 가드(60%)가 이를 막지 못함

5. 과도한 길이 증가 ({excessive_expansion_count}/{len(df)} = {excessive_expansion_count/len(df)*100:.1f}%)
   → 원문 대비 150% 이상 증가
   → 주로 반복 출력과 메타데이터 때문

핵심 교훈:
- Few-shot 자체는 효과가 있었다
- 문제는 "출력 형식 제어 실패"
- 후처리가 이를 해결하지 못함
- → 형식 제약 프롬프트로 전환 필요!
    """)

    # 결과 저장
    output_dir = Path(__file__).parent / "outputs" / "logs"
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "fewshot_v3_failure_analysis.txt", 'w', encoding='utf-8') as f:
        f.write(f"Few-shot v3 실패 원인 분석\n")
        f.write(f"="*80 + "\n\n")
        f.write(f"타겟 교정 성공률: {target_success_count}/{zero_recall_samples} ({target_success_count/zero_recall_samples*100:.1f}%)\n")
        f.write(f"메타데이터 출현: {metadata_count}/{len(df)} ({metadata_count/len(df)*100:.1f}%)\n")
        f.write(f"텍스트 반복: {repetition_count}/{len(df)} ({repetition_count/len(df)*100:.1f}%)\n")
        f.write(f"과도한 길이 증가: {excessive_expansion_count}/{len(df)} ({excessive_expansion_count/len(df)*100:.1f}%)\n")

    print(f"\n분석 결과 저장: {output_dir / 'fewshot_v3_failure_analysis.txt'}")


if __name__ == "__main__":
    analyze_fewshot_failure()
