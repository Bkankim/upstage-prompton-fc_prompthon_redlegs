"""
Baseline + MinimalRules Test 파일 생성
LB 제출용 submission CSV 생성
"""

import os
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from tqdm import tqdm

from src.prompts.baseline import BaselinePrompt
from src.postprocessors.minimal_rule import MinimalRulePostprocessor

# 환경변수 로드
load_dotenv()

def generate_test_submission():
    """
    Test 데이터로 LB 제출 파일 생성
    """
    # API 클라이언트 초기화
    api_key = os.getenv("UPSTAGE_API_KEY")
    if not api_key:
        raise ValueError("UPSTAGE_API_KEY not found in .env")

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.upstage.ai/v1"
    )

    # 프롬프트 및 후처리기 초기화
    prompt = BaselinePrompt()
    postprocessor = MinimalRulePostprocessor()

    # Test 데이터 로드
    test_df = pd.read_csv('data/test.csv')
    print(f"총 {len(test_df)}개 Test 데이터 교정 시작\n")

    # 교정 실행
    cor_sentences = []
    rule_applied_count = 0

    for idx, row in tqdm(test_df.iterrows(), total=len(test_df), desc="Test 교정"):
        err_sentence = row['err_sentence']

        try:
            # 1. Baseline으로 교정
            messages = prompt.to_messages(err_sentence)
            resp = client.chat.completions.create(
                model="solar-pro2",
                messages=messages,
                temperature=0.0,
            )
            baseline_output = resp.choices[0].message.content.strip()

            # 2. MinimalRulePostprocessor 적용
            final_output = postprocessor.process(err_sentence, baseline_output)

            # 규칙 적용 여부 확인
            if baseline_output.strip() == err_sentence.strip() and final_output.strip() != err_sentence.strip():
                rule_applied_count += 1
                print(f"\n[규칙 적용 {rule_applied_count}] ID: {row.get('id', idx)}")
                print(f"원문: {err_sentence}")
                print(f"규칙 후: {final_output}")

            cor_sentences.append(final_output)

        except Exception as e:
            print(f"\n오류 발생 (ID {idx}): {e}")
            cor_sentences.append(err_sentence)

    # 제출 파일 생성
    submission_df = pd.DataFrame({
        'id': test_df['id'],
        'err_sentence': test_df['err_sentence'],
        'cor_sentence': cor_sentences
    })

    # 저장
    os.makedirs('outputs/submissions/test', exist_ok=True)
    output_path = 'outputs/submissions/test/submission_baseline_minimal_rules_test.csv'
    submission_df.to_csv(output_path, index=False, encoding='utf-8-sig')

    print(f"\n\n=== Test 파일 생성 완료 ===")
    print(f"총 케이스: {len(test_df)}개")
    print(f"규칙 적용: {rule_applied_count}개")
    print(f"저장 경로: {output_path}")
    print(f"\n다음 단계: LB 제출")

if __name__ == "__main__":
    generate_test_submission()
