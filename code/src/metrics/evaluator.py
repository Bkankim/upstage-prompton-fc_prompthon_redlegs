"""
교정 결과 평가 모듈
Recall과 Precision 계산 로직 제공
"""

import pandas as pd
from typing import Dict

from .lcs import find_differences_with_offsets


def evaluate_correction(true_df: pd.DataFrame, pred_df: pd.DataFrame, n_samples: int = 5) -> Dict:
    """교정 결과 평가 및 점수 계산"""
    total_tp = 0
    total_fp = 0
    total_fm = 0
    total_fr = 0
    
    # 결과 분석을 위한 DataFrame 생성
    analysis_data = []
    
    for i in range(len(true_df)):
        sample = {
            'original': true_df.iloc[i]['err_sentence'],
            'golden': true_df.iloc[i]['cor_sentence'],
            'prediction': pred_df.iloc[i]['cor_sentence']
        }
        
        # 각 샘플별 점수 계산
        differences_og = find_differences_with_offsets(sample['original'], sample['golden'])
        differences_op = find_differences_with_offsets(sample['original'], sample['prediction'])
        
        og_idx = 0
        op_idx = 0
        tp = fp = fm = fr = 0
        
        while True:
            if og_idx >= len(differences_og) and op_idx >= len(differences_op):
                break
            if og_idx >= len(differences_og):
                fr += 1
                op_idx += 1
                continue
            if op_idx >= len(differences_op):
                fm += 1
                og_idx += 1
                continue
            if differences_og[og_idx][2] == differences_op[op_idx][2]:
                if differences_og[og_idx][1] == differences_op[op_idx][1]:
                    tp += 1
                else:
                    fp += 1
                og_idx += 1
                op_idx += 1
            elif differences_og[og_idx][2] < differences_op[op_idx][2]:
                fm += 1
                og_idx += 1
            elif differences_og[og_idx][2] > differences_op[op_idx][2]:
                fr += 1
                op_idx += 1
        
        # 분석 데이터에 추가 (개별 샘플별 세부 점수)
        analysis_data.append({
            'original': sample['original'],
            'golden': sample['golden'],
            'prediction': sample['prediction'],
            'tp': tp,
            'fp': fp,
            'fm': fm,
            'fr': fr
        })
        
        total_tp += tp
        total_fp += fp
        total_fm += fm
        total_fr += fr
    
    # 전체 점수 계산
    recall = total_tp / (total_tp + total_fp + total_fm) * 100 if (total_tp + total_fp + total_fm) > 0 else 0.0
    precision = total_tp / (total_tp + total_fp + total_fr) * 100 if (total_tp + total_fp + total_fr) > 0 else 0.0
    
    # 샘플 출력
    print("=== 평가 결과 ===")
    print(f"Recall: {recall:.2f}%")
    print(f"Precision: {precision:.2f}%\n")
    
    # 분석용 DataFrame 생성
    analysis_df = pd.DataFrame(analysis_data)
    
    return {
        'recall': recall,
        'precision': precision,
        'true_positives': total_tp,
        'false_positives': total_fp,
        'false_missings': total_fm,
        'false_redundants': total_fr,
        'analysis_df': analysis_df
    }
