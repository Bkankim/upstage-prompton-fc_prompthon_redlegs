"""
저장된 결과로 빠른 평가
"""

import pandas as pd
from src.evaluator import Evaluator

# Train 데이터 로드
train_df = pd.read_csv('data/train.csv')

# 결과 파일 로드
results_df = pd.read_csv('outputs/submissions/train/submission_baseline_minimal_rules.csv')

# 평가
evaluator = Evaluator()

true_df = pd.DataFrame({
    'err_sentence': train_df['err_sentence'],
    'cor_sentence': train_df['cor_sentence']
})

pred_df = pd.DataFrame({
    'err_sentence': results_df['err_sentence'],
    'cor_sentence': results_df['final_output']
})

eval_results = evaluator.evaluate(true_df, pred_df)

# 결과 출력
print(f"\n=== Baseline + MinimalRules 검증 결과 ===")
print(f"Recall: {eval_results['recall']:.2f}%")
print(f"Precision: {eval_results['precision']:.2f}%")
print(f"F1 Score: {eval_results['f1']:.2f}%")
print(f"\nTP: {eval_results['true_positives']}")
print(f"FP: {eval_results['false_positives']}")
print(f"FN: {eval_results['false_negatives']}")

# 결과 저장
import json
import os
os.makedirs('outputs/logs', exist_ok=True)
with open('outputs/logs/baseline_minimal_rules_train_results.json', 'w', encoding='utf-8') as f:
    json.dump({
        'recall': eval_results['recall'],
        'precision': eval_results['precision'],
        'f1': eval_results['f1'],
        'tp': eval_results['true_positives'],
        'fp': eval_results['false_positives'],
        'fn': eval_results['false_negatives'],
    }, f, ensure_ascii=False, indent=2)

print(f"\n결과 저장: outputs/logs/baseline_minimal_rules_train_results.json")
