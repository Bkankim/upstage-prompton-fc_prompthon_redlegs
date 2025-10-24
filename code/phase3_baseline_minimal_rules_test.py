"""
Baseline + MinimalRules Phase 3 회귀 테스트
이전 버전과 성능 비교
"""

import os
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from tqdm import tqdm

from src.prompts.baseline import BaselinePrompt
from src.postprocessors.minimal_rule import MinimalRulePostprocessor
from src.evaluator import Evaluator

# 환경변수 로드
load_dotenv()

def phase3_regression_test():
    """
    Phase 3 회귀 테스트 (62개 데이터)
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

    # Phase 3 데이터 로드
    phase3_df = pd.read_csv('data/test_phase3.csv')
    print(f"총 {len(phase3_df)}개 Phase 3 데이터 회귀 테스트 시작\n")

    # 교정 실행
    results = []
    rule_applied_count = 0

    for idx, row in tqdm(phase3_df.iterrows(), total=len(phase3_df), desc="Phase 3 교정"):
        err_sentence = row['err_sentence']
        cor_sentence = row['cor_sentence']

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

            results.append({
                'err_sentence': err_sentence,
                'cor_sentence': cor_sentence,
                'final_output': final_output
            })

        except Exception as e:
            print(f"\n오류 발생 (ID {idx}): {e}")
            results.append({
                'err_sentence': err_sentence,
                'cor_sentence': cor_sentence,
                'final_output': err_sentence
            })

    # 결과 DataFrame 생성
    results_df = pd.DataFrame(results)

    # 평가
    print(f"\n\n=== Phase 3 평가 시작 ===")
    evaluator = Evaluator()

    # True DataFrame 생성
    true_df = pd.DataFrame({
        'err_sentence': results_df['err_sentence'],
        'cor_sentence': results_df['cor_sentence']
    })

    # Prediction DataFrame 생성
    pred_df = pd.DataFrame({
        'err_sentence': results_df['err_sentence'],
        'cor_sentence': results_df['final_output']
    })

    eval_results = evaluator.evaluate(true_df, pred_df)

    # 결과 출력
    print(f"\n=== Phase 3 회귀 테스트 결과 ===")
    print(f"총 케이스: {len(phase3_df)}개")
    print(f"규칙 적용: {rule_applied_count}개")
    print(f"\nRecall: {eval_results['recall']:.2f}%")
    print(f"Precision: {eval_results['precision']:.2f}%")
    print(f"F1 Score: {eval_results['f1']:.2f}%")

    # 이전 버전과 비교
    print(f"\n=== 이전 버전 (Baseline) 비교 ===")
    print(f"Baseline Recall: 33.23% (Phase 3)")
    print(f"MinimalRules Recall: {eval_results['recall']:.2f}%")
    print(f"차이: {eval_results['recall'] - 33.23:.2f}%p")

    # 결과 저장
    os.makedirs('outputs/logs', exist_ok=True)
    import json
    with open('outputs/logs/baseline_minimal_rules_phase3_results.json', 'w', encoding='utf-8') as f:
        json.dump({
            'recall': eval_results['recall'],
            'precision': eval_results['precision'],
            'f1': eval_results['f1'],
            'tp': eval_results['true_positives'],
            'fp': eval_results['false_positives'],
            'fn': eval_results['false_negatives'],
            'total_cases': len(phase3_df),
            'rule_applied_count': rule_applied_count
        }, f, ensure_ascii=False, indent=2)

    print(f"\n결과 저장: outputs/logs/baseline_minimal_rules_phase3_results.json")

    return eval_results['recall']

if __name__ == "__main__":
    phase3_recall = phase3_regression_test()

    # 판정
    if phase3_recall >= 33.23:
        print(f"\n✅ Phase 3 통과! ({phase3_recall:.2f}% >= 33.23%)")
        print("다음 단계: Test 파일 생성 진행 가능")
    else:
        print(f"\n⚠️ Phase 3 성능 하락 ({phase3_recall:.2f}% < 33.23%)")
        print("Test 제출 전 재검토 필요")
