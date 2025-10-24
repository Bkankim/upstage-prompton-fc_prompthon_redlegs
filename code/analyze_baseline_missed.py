"""
Baseline이 놓치는 패턴 분석 스크립트
Train 데이터 샘플을 Baseline으로 교정하여 어떤 오류를 놓치는지 확인
"""

import pandas as pd
from src.prompts.baseline import BaselinePrompt
import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

def analyze_missed_patterns(sample_size=30):
    """
    Train 데이터 샘플을 Baseline으로 교정하고 놓친 패턴 분석
    """
    # Train 데이터 로드
    train_df = pd.read_csv('data/train.csv')

    # Baseline 프롬프트 초기화
    prompt = BaselinePrompt()

    # 결과 저장
    missed_cases = []

    print(f"총 {len(train_df)}개 중 {sample_size}개 샘플 분석 시작...")

    # 샘플 분석 (전체 데이터의 일부만)
    for idx, row in train_df.head(sample_size).iterrows():
        err_sentence = row['err_sentence']
        cor_sentence = row['cor_sentence']
        error_type = row['type']
        original_part = row['original_target_part']
        golden_part = row['golden_target_part']

        # Baseline으로 교정
        try:
            corrected = prompt.correct(err_sentence)

            # 원문 그대로인 경우 (교정하지 않은 경우)
            if corrected.strip() == err_sentence.strip():
                # 정답과 비교
                if corrected.strip() != cor_sentence.strip():
                    missed_cases.append({
                        'idx': idx,
                        'type': error_type,
                        'original': err_sentence,
                        'baseline_output': corrected,
                        'golden': cor_sentence,
                        'original_part': original_part,
                        'golden_part': golden_part
                    })
                    print(f"\n[{idx}] {error_type} - MISSED")
                    print(f"원문: {err_sentence[:100]}...")
                    print(f"오류부분: {original_part} → {golden_part}")
        except Exception as e:
            print(f"[{idx}] 오류 발생: {e}")
            continue

    # 결과 저장
    if missed_cases:
        missed_df = pd.DataFrame(missed_cases)
        missed_df.to_csv('outputs/analysis/baseline_missed_patterns.csv', index=False, encoding='utf-8-sig')
        print(f"\n\n=== 분석 완료 ===")
        print(f"총 {len(missed_cases)}개 케이스에서 Baseline이 교정 실패")
        print(f"결과 저장: outputs/analysis/baseline_missed_patterns.csv")

        # 오류 유형별 통계
        print("\n오류 유형별 놓친 케이스:")
        print(missed_df['type'].value_counts())

        # 명확한 패턴 추출
        print("\n\n=== 명확한 패턴 ===")
        for _, case in missed_df.iterrows():
            print(f"{case['original_part']} → {case['golden_part']} ({case['type']})")
    else:
        print("\n모든 케이스를 정확히 교정했습니다!")

if __name__ == "__main__":
    # outputs/analysis 디렉토리 생성
    os.makedirs('outputs/analysis', exist_ok=True)

    # 분석 실행 (30개 샘플)
    analyze_missed_patterns(sample_size=30)
